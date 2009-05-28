"""
This is a straight translation from Kinematics.{cpp,h} and NaoPose.{cpp,h}
from Northern Bites git repository, including ripping off the documentation
strings. Mainly as a self learning tool for their code.
With the ultimate goal of transforming vision x and y and object width
using joint angles and accelerometer inclination angles into
local coordinates (bearing and distance) to be fed into the
localization module, at first step to check the localization of northern
since I suspect they don't use the pitch correctly.
"""

import numpy
import math
from math import asin, hypot, atan, pi, atan2
from numpy import (sin, cos, zeros,
    tan, array, dot)
from numpy.linalg import norm
from scipy.linalg import lu, lu_factor

from burst_util import nicefloats, DeferredList
from burst.consts import HEAD_PITCH_JOINT_INDEX

from burst import options, field
from burst.consts import *
import burst

# TODO - pynaoqi'sm, should be factored out to some
# joint object that both burst and pynaoqi will use,
# inside burst. Like options.

# Notes on numpy usage with matrix math.
# I opted not to use the nicer matrix() * matrix() because
# of the annoyance of multiplying a matrix with a row, so
# instead:
# matrix by matrix:
#  dot(X,Y)
# matrix by row:
#  dot(X,row)
# matrix by col: same!
#  dot(X,col)

DEG_TO_RAD = pi/180.0

M_TO_CM  = 100.0
CM_TO_M  = 0.01
CM_TO_MM = 10.0
MM_TO_CM = 0.1

X_AXIS, Y_AXIS, Z_AXIS, W_AXIS = 0, 1, 2, 3
X, Y, Z = 0, 1, 2

(HEAD_CHAIN, LARM_CHAIN, LLEG_CHAIN, RLEG_CHAIN, RARM_CHAIN) = range(5)

EST_DIST, EST_ELEVATION, EST_BEARING, EST_X, EST_Y = range(5)

# TODO: UGLY
class Estimate(list):
    
    def __init__(self, v = None):
        if v is None:
            v = [0.0, 0.0, 0.0, 0.0, 0.0]
        if len(v) != 5:
            raise RuntimeError('Estimate must be made from a 5-tuple')
        super(Estimate, self).__init__(v)

    def get_dist(self):
        return self[EST_DIST]

    def set_dist(self, v):
        self[EST_DIST] = v
        
    dist = property(get_dist, set_dist)

    def get_elevation(self):
        return self[EST_ELEVATION]

    def set_elevation(self, v):
        self[EST_ELEVATION] = v

    elevation = property(get_elevation, set_elevation)

    def get_bearing(self):
        return self[EST_BEARING]

    def set_bearing(self, v):
        self[EST_BEARING] = v

    bearing = property(get_bearing, set_bearing)

    def get_x(self):
        return self[EST_X]

    def set_x(self, v):
        self[EST_X] = v
    
    x = property(get_x, set_x)

    def get_y(self):
        return self[EST_Y]

    def set_y(self, v):
        self[EST_Y] = v

    y = property(get_y, set_y)

    def __str__(self):
        return 'dist %3.3f, elevation %3.3f, bearing %3.3f, x %3.3f, y %3.3f' % (
            self.dist, self.elevation, self.bearing, self.x, self.y)

    def __repr__(self):
        return 'Estimate([%s, %s, %s, %s, %s])' % tuple(self)

NULL_ESTIMATE = Estimate()

## Matrix Utilities

def identity():
    return numpy.identity(4)

def translation4D(dx, dy, dz):
    m = identity()
    m[X_AXIS,W_AXIS] = dx
    m[Y_AXIS,W_AXIS] = dy
    m[Z_AXIS,W_AXIS] = dz
    return m

def vector4D(x, y, z, w=1.0):
    return array([x, y, z, w])

def rotation4D(axis, angle):
    rot = identity()
    sinAngle = sin(angle)
    cosAngle = cos(angle)
    if angle == 0.0:
        return rot;
    if axis == X_AXIS:
        rot[Y_AXIS, Y_AXIS] =  cosAngle
        rot[Y_AXIS, Z_AXIS] = -sinAngle
        rot[Z_AXIS, Y_AXIS] =  sinAngle
        rot[Z_AXIS, Z_AXIS] =  cosAngle
    elif axis == Y_AXIS:
        rot[X_AXIS, X_AXIS] =  cosAngle
        rot[X_AXIS, Z_AXIS] =  sinAngle
        rot[Z_AXIS, X_AXIS] = -sinAngle
        rot[Z_AXIS, Z_AXIS] =  cosAngle
    elif axis == Z_AXIS:
        rot[X_AXIS, X_AXIS] =  cosAngle
        rot[X_AXIS, Y_AXIS] = -sinAngle
        rot[Y_AXIS, X_AXIS] =  sinAngle
        rot[Y_AXIS, Y_AXIS] =  cosAngle
    return rot

def calculateForwardTransform(id, angles):
    """
    id - chain id
    angles - [float]
    """
    fullTransform = identity()

    # Do base transforms
    for baseTransform in BASE_TRANSFORMS[id]:
        fullTransform = dot(fullTransform, baseTransform)

    # Do mDH transforms
    numTransforms = NUM_JOINTS_CHAIN[id]
    for angle, (alpha, l, theta, d) in zip(angles, MDH_PARAMS[id]):
        # Right before we do a transformation, we are in the correct
        # coordinate frame and we need to store it, so we know where all the
        # links of a chain are. We only need to do this if the transformation
        # gives us a new link

        #length L - movement along the X(i-1) axis
        if l != 0:
            transX = translation4D(l,0.0,0.0)
            fullTransform = dot(fullTransform, transX)

        #twist: - rotate about the X(i-1) axis
        if alpha != 0:
            rotX = rotation4D(X_AXIS, alpha)
            fullTransform = dot(fullTransform, rotX)
      
        #theta - rotate about the Z(i) axis
        if theta + angle != 0:
            rotZ = rotation4D(Z_AXIS, theta + angle)
            fullTransform = dot(fullTransform, rotZ)
      
        #offset D movement along the Z(i) axis
        if d != 0:
            transZ = translation4D(0.0, 0.0, d)
            fullTransform = dot(fullTransform, transZ)
      
    # Do the end transforms
    for endTransform in END_TRANSFORMS[id]:
        fullTransform = dot(fullTransform, endTransform)
    
    return fullTransform

#### NaoPose

class NaoPose(object):
    """
     NaoPose: The class that is responsible for calculating the pose of the robot
     in order that the vision system can tell where the objects it sees are located
     with respect to the center of the body.
    
     To understand this file, please review the modified Denavit Hartenberg
     convention on robotics coordinate frame transformations, as well as the
     following documentation:
      * Nao Camera documentation
      * NaoWare documentation
      * HONG NUBots Enhancements to vision 2005 (for Horizon)
      * Wiki line-plane intersection:  en.wikipedia.org/wiki/Line-plane_intersection
    
     The following coordinate frames will be important:
      * The camera frame. origin at the focal point, alligned with the head.
      * The body frame. origin at the center of mass (com), alligned with the torso.
      * The world frame. orgin at the center of mass, alligned with the ground
      * The horizon frame. origin at the focal point, alligned with the ground
    
     The following methods are central to the functioning of NaoPose:
      * tranform()     - must be called each frame. setups transformation matrices
                         for the legs and the camera, which enables calculation of
                         body height and horizon
    
      * pixEstimate()  - returns an estimate to a given x,y pixel, representing an
                         object at a certain height from the ground. Takes units of
                         CM, and returns in CM. See also bodyEstimate
    
      * bodyEstimate() - returns an estimate for a given x,y pixel, and a distance
                         calculated from vision by blob size. See also pixEstimate
    
    
      * Performance Profile: mDH for 3 chains takes 70% time in tranform(), and
                             horizon caculation takes the other 30%. pixEstimate()
                             and bodyEstimate() take two orders of magnitude less
                             time than transform()
      * Optimization: Eventually we'll calculate the world frame rotation using
                      gyros, so we won't need to use the support leg's orientation
                      in space to figure this out. That will save quite a bit of
                      computation.
    
     @date July 2008
     @author George Slavov
     @author Johannes Strom
    
     TODO:
       - Need to fix the world frame, since it currently relies on the rotation of
         the foot also about the Z axis, which means when we are turning, for
         example, we will report distances and more imporantly bearings relative
         to the foot instead of the body. This has been hacked for now, in
         bodyEstimate.
    
       - While testing this code on the robot, we saw a significant, though
         infrequent, jump in the estimate for the horizon line. The cause could be
         one of bad joint information from the motion engine, a singular matrix
         inversion we do somewhere in the code, or something completely different.
         Needs to be looked at.
    
       - While testing this code on the robot, we have noticed severe
         discrepancies between distances reported from pixEstimate, and their
         actual values. While the model seems to work well in general, there
         needs to be a serious evaluation of these defects, since these
         inaccuracies will have serious consequences for localization.
    
    """

    def __init__(self):
        self.cameraToWorldFrame = identity()
        self.focalPointInWorldFrame = identity()
        self.comHeight = 0 # MM cause that's the way they do it.
        self.cameraToHorizonFrame = identity()
        self.horizonSlope = 0.0
        self.horizonLeft = [0.0, 0.0]
        self.horizonRight = [0.0, 0.0]
        self._inclination_vars = [
            'Device/SubDeviceList/InertialSensor/AngleX/Sensor/Value',
            'Device/SubDeviceList/InertialSensor/AngleY/Sensor/Value']
        self._inclination = [0.0, 0.0]
        self.transform([0.0]*26, [0.0,0.0]) # init stuff
        self._connecting_to_webots = burst.connecting_to_webots()
        self._location = None
        self._ball_location = None

    # Helper Pynaoqi functions

    def updateLocations(self, con):
        """ Call update and return pairs of coordinates for interesting points.
        Later return objects that contain:
         * last known location
         * location computation trail: this is mainly debugging, but it will
          become a powerful tool for determining how to use the location, it should
          be a succint explanation how NaoPose computed the current location:
           - last frame saw all yellow goal (SAYG)
           - 10 frames ago SAYG, stood still and turned head since then
           - -10 SAYG, 5f stood still, 5f odo said 2 steps forward.
           - friend?
        """
        def returnPairs(result):
            results = []
            if self._location:
                #print "x %3.3f y %3.3f theta %3.3f" % self._location
                results.append(self._location[:2])
            return results

        return self.update(con, returnPairs)

    def update(self, con, cb=None):
        """ Development helper. Not to be confused with player usable code.
        """
        from pynaoqi.shell import onevision
        d = DeferredList([
            con.ALMemory.getListData(self._inclination_vars).addCallback(self._storeInclination),
            con.ALMotion.getBodyAngles().addCallback(self._storeBodyAngles),
            onevision().addCallback(self._storeVision),
            ]).addCallback(self._calcValues)
        if cb is None:
            cb = self._printUpdatedCalculations
        d.addCallback(cb)
        return d

    def _storeInclination(self, result):
        if not self._connecting_to_webots:
            self._inclination = result

    def _storeBodyAngles(self, result):
        self._bodyAngles = result

    def _storeVision(self, result):
        self._v = result

    def _printUpdatedCalculations(self, result):
        print "inclination:", nicefloats(self._inclination)
        print "joints:     ", nicefloats(self._bodyAngles)
        print "comheight:  ", self.comHeight
        print "focal WF:   ", self.focalPointInWorldFrame
        print "cameraToWF: ", (self.cameraToWorldFrame*100).astype('int')
        print
        v = self._v
        for name, obj in [('YGLP', v.YGLP),
                    ('YGRP', v.YGRP), ('Ball', v.Ball)]:
            estimate, dist_height = self._estimates[name]
            print "mine: pix=%3.3f, height=%3.3f, given: focDist=%3.3f, dist=%3.3f" % (
                estimate.dist, dist_height, obj.focdist, obj.distance)
            print "mine: bearing=%3.3f, given: bearing=%3.3f" % (
                estimate.bearing*180.0/pi, obj.bearingdeg)
        if self._location:
            x, y, theta = self._location
            theta *= 180.0/pi
            print "Location: %3.3f %3.3f %3.3f" % (x, y, theta)

    def _returnDistances(self, _):
        """ Tester for pixHeightToDistancePlus. To run do in pynaoqi:
        import burst.kinematics as kin
        loop(lambda: kin.pose.update(con, kin.pose._returnDistances).addCallback(nicefloats), dt=0.5)
        """
        def one(obj):
            return self.pixHeightToDistancePlus(obj.height, obj.x, field.GOAL_POST_CM_HEIGHT, debug=True)
        return one(self._v.YGRP) + one(self._v.YGLP)

    def _calcValues(self, result):
        # update the transforms
        self.transform(self._bodyAngles, self._inclination)
        # calculate various objects distances
        v = self._v
        self._estimates = estimates = {}
        goal_post_height = field.GOAL_POST_CM_HEIGHT
        for name, obj, objheight_cm in [
            ('YGLP', v.YGLP, goal_post_height),
            ('YGRP', v.YGRP, goal_post_height), ('Ball', v.Ball, 10)]:
            if obj.distance == 0.0:
                continue
            if name == 'Ball':
                x, y = obj.centerx, obj.centery # ball doesn't record the bottom x and y
            else:
                x, y = obj.x, obj.y
            estimate = self.pixEstimate(x, y, 0.0)
            # pixHeightToDistancePlus DOESN'T WORK - solution right now is to only use
            # value of pixel when the object is in bearing=0
            #dist_height = self.pixHeightToDistancePlus(obj.height, x,
            #    objheight_cm)
            dist_height = self.pixHeightToDistance(obj.height, objheight_cm)
            estimates[name] = (estimate, dist_height)
        # Try to calculate our position in WF
        self._updateXYTheta_from_twoDistOneAngle()

    def _updateXYTheta_from_twoDistOneAngle(self,
            top=None, bottom=None, debug=False):
        """ Take two objects and update our self location in WF from it.
        NOTE: the objects need to be ordered - top_y > bottom_y
        
        Defaults to Yellow Goal Left Post and Right Post (Top and Bottom
        respectively)
        """
        if top is not None or bottom is not None:
            raise NotIMplementedError('Not done yet')
        yglp, ygrp = self._v.YGLP, self._v.YGRP
        if yglp.distance != 0.0 and ygrp.distance != 0.0:
            (e_left, r1), (e_right, r2) = (
                self._estimates['YGLP'],
                self._estimates['YGRP'])
            p0 = field.yellow_goal.top_post.xy
            p1 = field.yellow_goal.bottom_post.xy
            d = field.CROSSBAR_CM_WIDTH / 2.0
            # XXX: I think the YGLP is the BOTTOM, not the TOP
            if e_right.dist == 0.0:
                #print "using given bearing"
                a1 = ygrp.bearingdeg * pi / 180.0
            else:
                a1 = e_right.bearing
            x, y, theta = self.xyt_from_two_dist_one_angle(
                r1=r1, r2=r2, a1=a1, d=d, p0=p0, p1=p1, debug=debug)
            self._location = (x, y, theta)
            return x, y, theta
        return None

    # New Code! High level computations - compute world location (x,y,theta)
    # from visual landmarks
    def xyt_from_two_dist_one_angle(self, r1, r2, a1, d, p0, p1, debug=False):
        """ Compute the location given two distances to known landmarks and
        one angle to one of them. To be used with two posts, but would work
        equally for any two things.  The computation is done in the Objects
        Frame (OF), but returned in the World Frame (WF) in which p0 = (x0,
        y0) and p1 = (x1, y1) are defined.

        The OF is defined as follows: origin lies in the midsection of the
        line connecting p0 and p1, d is half the distance to the first. Y is
        the axis connecting p1 to p0, X is to the right.

               (x0,y0) 0    -d- H   O     -d-     1 (x1,y1)
                      /      ,-'           ,-----'
                     /  a1,-'       ,-----'
                    /  ,-'  ,------'
                   /,------'
                  X (x,y)

        H is the intersection of the heading and the p0-p1 line.

        a1 must be positive clockwise, zero if in the middle of the frame
        (i.e. at the same direction as the bearing)

        Also, |r1 - r2| <= 2*d must hold.. if it doesn't, caller
        needs to rethink it's inputs.

        RETURN VALUE: (None, None, None) on error, (x,y,theta) otherwise
        """
        if abs(r1 - r2) > 2 * d:
            return (None, None, None)
        x0, y0 = p0;        x1, y1 = p1
        O = ((x0 + x1) / 2, (y0 + y1)/2) # position of the origin in WF
        #assert(almost_equal(4*d**2, (x1 - x0)**2 + (y1 - y0)**2))

        # Compute in OF

        if debug:
            import pdb; pdb.set_trace()

        # first x,y
        r1_2 = r1**2
        r2_2 = r2**2
        y = ( r2_2 - r1_2 ) / 4 / d
        x = - ( r1_2 - (y - d)**2 )**0.5
        # then theta (heading)
        gamma = atan2(y - d, -x)
        theta = gamma + a1

        # Transform back into WF

        # Optimize for no rotation case
        if x0 != x1:
            two_d = 2 * d
            delta_x, delta_y = x1 - x0, y1 - y0
            y_unit_x, y_unit_y = delta_x / two_d, delta_y / two_d
            x_unit_x, x_unit_y = -y_unit_y, y_unit_x
            # Rotate
            _x = ( x_unit_x ) * x + ( y_unit_x ) * y
            _y = ( x_unit_y ) * x + ( y_unit_y ) * y
            x, y = _x, _y
            # rotate the heading - TODO: be nice to not need a tan^-1 here.
            # TODO - not accurate for delta_x << 1 
            obj_theta = atan2(x_unit_y, x_unit_x)
            theta += obj_theta
        # Translate
        x, y = O[0] + x, O[1] + y
        return x, y, -theta

    def pixHeightToDistancePlus(self, pixHeight, pix_x, cmHeight,
            debug=False, verbose=False):
        """
        approx. the same as ground plane intersection - actually
        should give the same results.

        h - object height
        f - focal distance in mm
        b - object height on the ccd in mm
        c - object distance from image center along x axis on ccd in mm
        x - distance of object center on ccd along x axis (perpendicular
         to the height axis). Note that this is geared for the nao,
         which only has pitch and no roll for the camera, assuming the body
         frame is parallel to the ground (which should also be correct as
         long as the robot isn't falling).
        """
        # TODO - do another calculation using the joint poses
        # to make sure we are actually parallel to the ground - we
        # already have the matrix. (cameraFrameToWorld or something)

        # The joint has reversed sign compared to the camera's built in pitch.
        pitch = CAMERA_PITCH_ANGLE + self._bodyAngles[HEAD_PITCH_JOINT_INDEX]
        observed_height = cmHeight * cos(pitch)
        if verbose:
            print "pitch deg = %3.3f, cmHeight = %3.3f, observed_height = %3.3f" % (
                pitch * 180.0 / pi, cmHeight, observed_height)
        f = FOCAL_LENGTH_MM
        c = PIX_X_TO_MM * (pix_x - IMAGE_WIDTH/2.0)
        f_tilde = (c**2 + f**2)**0.5
        if verbose:
            print "c [mm]    = %3.3f, f [mm]   = %3.3f, f_tilde         = %3.3f" % (
            c, f, f_tilde)
        dist = observed_height * f_tilde / (pixHeight * PIX_Y_TO_MM)
        if verbose:
            print "dist = %3.3f. no pitch dist = %3.3f, no bearing dist = %3.3f" % (
                dist, dist / cos(pitch), dist / cos(pitch) / f_tilde * f)
        if debug:
            return dist, dist / cos(pitch), dist / cos(pitch) / f_tilde * f
        return dist

    def bearingFromPix(self, x, y):
        raise NotImplementedError('TODO')

    # NaoPose.cpp 

    def transform(self, bodyAngles, inclinationAngles, supportLegChain=LLEG_CHAIN, debug=False):
        """
        TOOD: get supportFoot from ALMotion (if it is our own walk engine should
        be easier)

        Calculate all forward transformation matrices from the center of mass to each
        end effector. For the head this is the focal point of the camera. We also
        calculate the transformation from the camera frame to the world frame.
        Then we calculate horizon and camera height which is necessary for the
        calculation of pix estimates.
        """

        if debug:
            import pdb; pdb.set_trace()

        # Make up bogus values
        HEAD_START, LLEG_START, RLEG_START = 0, 8, 14
        headAngles = bodyAngles[HEAD_START:2]
        lLegAngles = bodyAngles[LLEG_START:LLEG_START+6]
        rLegAngles = bodyAngles[RLEG_START:RLEG_START+6]

        origin = vector4D(0.0, 0.0, 0.0)

        cameraToBodyTransform = calculateForwardTransform(HEAD_CHAIN, headAngles)

        leg_angles = (supportLegChain == LLEG_CHAIN and lLegAngles) or rLegAngles
        supportLegToBodyTransform = calculateForwardTransform(
                    supportLegChain, leg_angles)

        supportLegLocation = dot(supportLegToBodyTransform, origin)

        # At this time we trust inertial
        bodyInclinationX, bodyInclinationY = inclinationAngles

        bodyToWorldTransform = dot(rotation4D(X_AXIS, bodyInclinationX),
                rotation4D(Y_AXIS, bodyInclinationY))
      
        torsoLocationInLegFrame = dot(bodyToWorldTransform, supportLegLocation)
        # get the Z component of the location
        self.comHeight = -torsoLocationInLegFrame[Z]
      
        self.cameraToWorldFrame = cameraToWorldFrame = dot(
            bodyToWorldTransform, cameraToBodyTransform)
      
        self.calcImageHorizonLine()
        self.focalPointInWorldFrame = [cameraToWorldFrame[X,3],
            cameraToWorldFrame[Y,3], cameraToWorldFrame[Z,3]]
        return self.focalPointInWorldFrame

    def calcImageHorizonLine(self):
        """
         Calculates a horizon line for real image via the camera matrix which is a
         global member of NaoPose. The line is stored as two endpoints on the left and
         right of the screen in horizonLeft and horizonRight.
        """
        # Moving the camera frame to the center of the body lets us compare the
        # rotation of the camera frame relative to the world frame.
        cameraToHorizonFrame = array(self.cameraToWorldFrame)
        self.cameraToHorizonFrame = cameraToHorizonFrame

        cameraToHorizonFrame[X_AXIS, W_AXIS] = 0.0
        cameraToHorizonFrame[Y_AXIS, W_AXIS] = 0.0
        cameraToHorizonFrame[Z_AXIS, W_AXIS] = 0.0

        # We need the inverse but we calculate the transpose because they are
        # equivalent for orthogonal matrices and transpose is faster.
        horizonToCameraFrame = cameraToHorizonFrame.T

        # We defined each edge of the CCD as a line, and solve
        # for where that line intersects the horizon plane ( xy plane level with the
        # ground, at the height of the focal point
        leftEdge = [dot(cameraToHorizonFrame, topLeft),
                    dot(cameraToHorizonFrame, bottomLeft)]

        rightEdge = [dot(cameraToHorizonFrame, topRight),
                     dot(cameraToHorizonFrame, bottomRight)]

        #intersection points in the horizon frame
        #intersectionLeft = []
        #intersectionRight = []

        #try {
        #  intersectionLeft = intersectLineWithXYPlane(leftEdge);
        #  intersectionRight = intersectLineWithXYPlane(rightEdge);
        ##} catch (boost::numeric::ublas::internal_logic* const e) {
        #} catch (...) {
        ## TODO: needs to fix this thoroughly...
        #  std::cout << "ERROR: intersectLineWithXYPlane threw an exception, trying to cope..." << std::endl;
        #}

        ## Now they are in the camera frame. Result still stored in intersection 1,2
        #intersectionLeft = prod(horizonToCameraFrame, intersectionLeft);
        #intersectionRight = prod(horizonToCameraFrame, intersectionRight);

        ##we are only interested in the height (z axis), not the width

        #const float height_mm_left = intersectionLeft[Z];
        #const float height_mm_right = intersectionRight[Z];
      
        # TODO: Temp fix for BURST:
        height_mm_left = IMAGE_HEIGHT_MM/2
        height_mm_right = IMAGE_HEIGHT_MM/2
      
        height_pix_left = -height_mm_left*MM_TO_PIX_Y + IMAGE_HEIGHT/2
        height_pix_right = -height_mm_right*MM_TO_PIX_Y + IMAGE_HEIGHT/2
      
        #cout << "height_mm_left: " << height_mm_left << endl;
        #cout << "height_mm_right: " << height_mm_right << endl;
        #cout << "height_pix_left: " << height_pix_left << endl;
        #cout << "height_pix_right: " << height_pix_right << endl;
      
        self.horizonLeft[:] = 0.0, round(height_pix_left)
        self.horizonRight[:] = IMAGE_WIDTH - 1, round(height_pix_right)
      
        self.horizonSlope = float((height_pix_right - height_pix_left) /(IMAGE_WIDTH -1.0))
      
        #cout << "horizonSlope: " << horizonSlope << endl;
      
        if self.horizonSlope != 0:
            perpenHorizonSlope = -1/self.horizonSlope
        else:
            perpenHorizonSlope = INFTY

    def intersectLineWithXYPlane(aLine):
        """
         Method to take a vector of two points describing a line, and intersect it with
         the XYplane of the relevant coordinate frame. Could probably be made faster
         if dependency on matrix multiplication was removed.
        """
        l1, l2 = aLine[0], aLine[1]

        #points on the plane level with the ground in the horizon coord frame
        #normally need 3 points, but since one is the origin, it can get ignored
        unitX = vector4D(1,0,0)
        unitY = vector4D(0,1,0)
      
        #we now solve the point of intersection using linear algebra
        #Ax=b, where b is the target, x is the solution of weights (t,u,v)
        #to solve l1 + (l2 -l1)t = o1*u + o2*v
        #Note!: usually a plane is defined by three vectors. e.g. in this case of
        #the target plane goes through the origin of the target
        #frame, so one of the vectors is the zero vector, so we ignore it
        #See http://en.wikipedia.org/wiki/Line-plane_intersection for detail
        eqSystem = zeros((3,3))
        eqSystem[0,0]=l1[0] - l2[0]; eqSystem[0,1] = unitX[0]; eqSystem[0,2]=unitY[0];
      
        eqSystem[1,0]=l1[1] - l2[1]; eqSystem[1,1] = unitX[1]; eqSystem[1,2]=unitY[1];
      
        eqSystem[2,0]=l1[2] - l2[2]; eqSystem[2,1] = unitX[2]; eqSystem[2,2]=unitY[2];
      
        # Solve for the solution of the weights.
        # Now usually we would solve eqSystem*target = l1 for target, but l1 is
        # defined in homogeneous coordiantes. We need it to be a 3 by 1 vector to
        # solve the system of equations.
        target = array(l1)
        lu, piv = lu_factor(eqSystem)
        # TODO: check the lu and piv like singularRow check in original code

        # If the matrix is near singular, this value will be != 0
        #singularRow = dot(m,lu_solve(lu_factor(m),[0,1]))lu_factorize(eqSystem, P)
        #if (singularRow != 0) {
        #  # The camera is parallel to the ground
        #  # Since l1 is the top (left/right) of the image, the horizon
        #  # will be at the top of the screen in this case which works for us.
        #  return l1;
        #}
      
        result = lu_solve((lu, piv), target)
        t = result[0]
      
        #the first variable in the linear equation was t, so it appears at the top of
        #the vector 'result'. The 't' is such that the point l1 + (l2 -l1)t is on
        #the horizon plane
        #NOTE: this intersection is still in the horizon frame though
        intersection = l2 - l1
        intersection *= t
        intersection += l1
      
        # The intersection seems to currently have the wrong y coordinate. It's the
        # negative of what it should be.
        return intersection

    def pixEstimate(self, pixelX, pixelY, objectHeight, debug=False):
        """
         returns an estimate to a given x,y pixel, representing an
                         object at a certain height from the ground. Takes units of
                         CM, and returns in CM. See also bodyEstimate
         """

        if debug:
            import pdb; pdb.set_trace()

        if (pixelX >= IMAGE_WIDTH or pixelX < 0 or
            pixelY >= IMAGE_HEIGHT or pixelY < 0):
            return NULL_ESTIMATE

        # declare x,y,z coordinate of pixel in relation to focal point
        pixelInCameraFrame = vector4D(FOCAL_LENGTH_MM,
                 (IMAGE_CENTER_X - float(pixelX)) * PIX_X_TO_MM,
                 (IMAGE_CENTER_Y - float(pixelY)) * PIX_Y_TO_MM)

        # Declare x,y,z coordinate of pixel in relation to body center
        # transform camera coordinates to body frame coordinates for a test pixel
        pixelInWorldFrame = dot(self.cameraToWorldFrame, pixelInCameraFrame)

        # Draw the line between the focal point and the pixel while in the world
        # frame. Our goal is to find the point of intersection of that line and
        # the plane, parallel to the ground, passing through the object height.
        # In most cases, this plane is the ground plane, which is comHeight below the
        # origin of the world frame. If we call this method with objectHeight != 0,
        # then the plane is at a different height.
        object_z_in_world_frame = -self.comHeight + objectHeight * CM_TO_MM

        # We are going to parameterize the line with one variable t. We find the t
        # for which the line goes through the plane, then evaluate the line at t for
        # the x,y,z coordinate
        t = 0

        # calculate t knowing object_z_in_body_frame
        if ((self.focalPointInWorldFrame[Z] - pixelInWorldFrame[Z]) != 0):
            t = ( object_z_in_world_frame - pixelInWorldFrame[Z]
                ) / ( self.focalPointInWorldFrame[Z] - pixelInWorldFrame[Z] )

        x = pixelInWorldFrame[X] + (
            self.focalPointInWorldFrame[X] - pixelInWorldFrame[X])*t
        y = pixelInWorldFrame[Y] + (
            self.focalPointInWorldFrame[Y] - pixelInWorldFrame[Y])*t
        z = pixelInWorldFrame[Z] + (
            self.focalPointInWorldFrame[Z] - pixelInWorldFrame[Z])*t
        objectInWorldFrame = vector4D(x,y,z)

        # SANITY CHECKS
        #If the plane where the target object is, is below the camera height,
        #then we need to make sure that the pixel in world frame is lower than
        #the focal point, or else, we will get odd results, since the point
        #of intersection with that plane will be behind us.
        if (objectHeight*CM_TO_MM < self.comHeight + self.focalPointInWorldFrame[Z]
            and pixelInWorldFrame[Z] > self.focalPointInWorldFrame[Z]):
            return NULL_ESTIMATE

        est = self.getEstimate(objectInWorldFrame)
        est[EST_DIST] = correctDistance(est[EST_DIST])

        return est


    def bodyEstimate(self, x, y, dist, USE_WEBOTS_ESTIMATE=True):
        """
        Body estimate takes a pixel on the screen, and a vision calculated
        distance to that pixel, and calculates where that pixel is relative
        to the world frame.  It then returns an estimate to that position,
        with units in cm. See also pixEstimate
        """
        if dist <= 0.0:
            return NULL_ESTIMATE

        #all angle signs are according to right hand rule for the major axis
        # get bearing angle in image plane,left pos, right negative
        object_bearing = (IMAGE_CENTER_X - float(x))*PIX_TO_RAD_X
        # get elevation angle in image plane, up negative, down is postive
        object_elevation = (float(y) - IMAGE_CENTER_Y)*PIX_TO_RAD_Y
        # convert dist estimate to mm
        object_dist = dist*10

        # object in the camera frame
        objectInCameraFrame = vector4D(
            object_dist*cos(object_bearing)*cos(-object_elevation),
                 object_dist*sin(object_bearing),
                 object_dist*cos(object_bearing)*sin(-object_elevation))

        # object in world frame
        objectInWorldFrame = dot(cameraToWorldFrame, objectInCameraFrame)

        objectInBodyFrame = dot(cameraToBodyTransform, objectInCameraFrame)

        if USE_WEBOTS_ESTIMATE:
            badBearing = self.getEstimate(objectInWorldFrame)
            goodBearing = self.getEstimate(objectInBodyFrame)
            #cout << goodBearing[EST_BEARING] << "\t" << badBearing[EST_BEARING] << endl;
            goodEst = Estimate([badBearing[EST_DIST],
                       goodBearing[EST_ELEVATION],
                       goodBearing[EST_BEARING],
                       badBearing[EST_X],
                       badBearing[EST_Y]])

            return goodEst
        else:
            return self.getEstimate(objectInWorldFrame)

    def getEstimate(self, objInWorldFrame):
        """
        Method to populate an estimate with an vector4D in homogenous coordinates.

        Input units are MM, output in estimate is in CM, radians
        """
        pix_est = Estimate()

        # distance as projected onto XY plane - ie bird's eye view

        pix_est[EST_DIST] = hypot(
            objInWorldFrame[X], objInWorldFrame[Y]) * MM_TO_CM

        # calculate in radians the bearing to the object from the center of the body
        # since trig functions can't handle 2 Pi, we need to differentiate
        # by quadrant:

        yPos = objInWorldFrame[Y] >= 0
        xPos = objInWorldFrame[X] >= 0
        temp = objInWorldFrame[Y] / objInWorldFrame[X]
        if (temp != 0):
            # quadrants +x,+y and +x-y
            if( xPos and (yPos or not yPos) ):
                pix_est[EST_BEARING] = atan(temp)
            elif yPos: # quadrant -x+y
                pix_est[EST_BEARING] = atan(temp) + pi
            else:      # quadrant -x+y
                pix_est[EST_BEARING] = atan(temp) - pi

        pix_est[EST_X] = objInWorldFrame[X] * MM_TO_CM
        pix_est[EST_Y] = objInWorldFrame[Y] * MM_TO_CM

        # need dist in 3D for angular elevation, not birdseye
        dist3D = norm(objInWorldFrame) # in MM
        temp2 = objInWorldFrame[Z] / dist3D
        if (temp2 <= 1.0):
            pix_est[EST_ELEVATION] = asin(temp2)

        return pix_est

    def pixHeightToDistance(self, pixHeight, cmHeight):
        """
        Return the distance to the object based on the image magnification of its
        height
        """
        return (FOCAL_LENGTH_MM / (pixHeight * PIX_Y_TO_MM)) * cmHeight

    def pixWidthToDistance(self, pixWidth, cmWidth):
        """
        Return the distance to the object based on the image magnification of its
        height
        """
        return (FOCAL_LENGTH_MM / (pixWidth * PIX_X_TO_MM)) * cmWidth

def correctDistance(uncorrectedDist):
    return (-0.000591972 * uncorrectedDist * uncorrectedDist +
        0.858283 * uncorrectedDist + 2.18768)


# Numerics
INFTY = 1E+37

# Screen edge coordinates in the camera coordinate frame
topLeft = vector4D(FOCAL_LENGTH_MM, IMAGE_WIDTH_MM/2, IMAGE_HEIGHT_MM/2)
bottomLeft = vector4D(FOCAL_LENGTH_MM, IMAGE_WIDTH_MM/2, -IMAGE_HEIGHT_MM/2)
topRight = vector4D(FOCAL_LENGTH_MM, -IMAGE_WIDTH_MM/2, IMAGE_HEIGHT_MM/2)
bottomRight = vector4D(FOCAL_LENGTH_MM, -IMAGE_WIDTH_MM/2, -IMAGE_HEIGHT_MM/2)

# Kinematics

SHOULDER_OFFSET_Y = 98.0
UPPER_ARM_LENGTH = 90.0
LOWER_ARM_LENGTH = 145.0
SHOULDER_OFFSET_Z = 100.0
THIGH_LENGTH = 100.0
TIBIA_LENGTH = 100.0
NECK_OFFSET_Z = 126.5
HIP_OFFSET_Y = 50.0
HIP_OFFSET_Z = 85.0
FOOT_HEIGHT = 46.0

# Bottom Camera
CAMERA_OFF_X = 48.80 # in millimeters
CAMERA_OFF_Z = 23.81  # in millimeters
CAMERA_PITCH_ANGLE = 40.0 * DEG_TO_RAD # 40 degrees

#*********       Joint Bounds       ***********/
HEAD_BOUNDS = [[-2.09,2.09],[-.785,.785]]

# Order of arm joints: ShoulderPitch, SRoll, ElbowYaw, ERoll
LEFT_ARM_BOUNDS = [[-2.09,2.09],
    [0.0,1.65],
    [-2.09,2.09],
    [-1.57,0.0]
    ,[-1.832, 1.832],
        [0.0, 0.0]
]
RIGHT_ARM_BOUNDS = [[-2.09,2.09],
    [-1.65,0.0],
    [-2.09,2.09],
    [0.0,1.57]
    ,[-1.832, 1.832],
        [0.0, 0.0]
]

# Order of leg joints: HYPitch HipPitch HipRoll KneePitch APitch ARoll
LEFT_LEG_BOUNDS = [[-1.57,0.0],
    [-1.57,.436],
    [-.349,.785],
    [0.0,2.269],
    [-1.309,.524],
    [-.785,.349]
]
RIGHT_LEG_BOUNDS = [[-1.57,0.0],
    [-1.57,.436],
    [-.785,.349],
    [0.0,2.269],
    [-1.309,.524],
    [-.349,.785]]

#*********     joint velocity limits **********/
#Set hardware values- nominal speed in rad/20ms
#from $AL_DIR/doc/reddoc
#M=motor r = reduction ratio

M1R1_NOMINAL = 0.0658
M1R2_NOMINAL = 0.1012
M2R1_NOMINAL = 0.1227
M2R2_NOMINAL = 0.1065

M1R1_NO_LOAD = 0.08308
M1R2_NO_LOAD = 0.1279
M2R1_NO_LOAD = 0.16528
M2R2_NO_LOAD = 0.1438

M1R1_AVG = (M1R1_NOMINAL + M1R1_NO_LOAD )*0.5
M1R2_AVG = (M1R2_NOMINAL + M1R2_NO_LOAD )*0.5
M2R1_AVG = (M2R1_NOMINAL + M2R1_NO_LOAD )*0.5
M2R2_AVG = (M2R2_NOMINAL + M2R2_NO_LOAD )*0.5

jointsMaxVelNominal = [
#head
    M2R2_NOMINAL, M2R1_NOMINAL,
#left arm
    M2R1_NOMINAL, M2R2_NOMINAL, M2R1_NOMINAL, M2R2_NOMINAL,
    M1R1_NOMINAL, M1R1_NOMINAL,
#left leg
    M1R1_NOMINAL, M1R1_NOMINAL, M1R2_NOMINAL,
    M1R2_NOMINAL, M1R2_NOMINAL, M1R1_NOMINAL,
#right leg
    M1R1_NOMINAL, M1R1_NOMINAL, M1R2_NOMINAL,
    M1R2_NOMINAL, M1R2_NOMINAL, M1R1_NOMINAL,
#right arm
    M2R2_NOMINAL, M2R2_NOMINAL, M2R1_NOMINAL, M2R2_NOMINAL
        ,M1R1_NOMINAL, M1R1_NOMINAL
]

jointsMaxVelNoLoad = [
#head
    M2R2_NO_LOAD, M2R1_NO_LOAD,
#left arm
    M2R1_NO_LOAD, M2R2_NO_LOAD, M2R1_NO_LOAD, M2R2_NO_LOAD,
    M1R1_NO_LOAD, M1R1_NO_LOAD,
#left leg
    M1R1_NO_LOAD, M1R1_NO_LOAD, M1R2_NO_LOAD,
    M1R2_NO_LOAD, M1R2_NO_LOAD, M1R1_NO_LOAD,
#right leg
    M1R1_NO_LOAD, M1R1_NO_LOAD, M1R2_NO_LOAD,
    M1R2_NO_LOAD, M1R2_NO_LOAD, M1R1_NO_LOAD,
#right arm
    M2R2_NO_LOAD, M2R2_NO_LOAD, M2R1_NO_LOAD, M2R2_NO_LOAD
        ,M1R1_NO_LOAD, M1R1_NO_LOAD
]

jointsMaxVelAvg = [
#head
    M2R2_AVG, M2R1_AVG,
#left arm
    M2R1_AVG, M2R2_AVG, M2R1_AVG, M2R2_AVG,
    M1R1_AVG, M1R1_AVG,
#left leg
    M1R1_AVG, M1R1_AVG, M1R2_AVG,
    M1R2_AVG, M1R2_AVG, M1R1_AVG,
#right leg
    M1R1_AVG, M1R1_AVG, M1R2_AVG,
    M1R2_AVG, M1R2_AVG, M1R1_AVG,
#right arm
    M2R2_AVG, M2R2_AVG, M2R1_AVG, M2R2_AVG
        ,M1R1_AVG, M1R1_AVG
]


#*********      mDH parameters      ***********/

#mDHNames
ALPHA, L, THETA, D = 0, 1, 2, 3

#                                  (alpha,  a ,  theta ,   d  )
HEAD_MDH_PARAMS = [[0.0 , 0.0,  0.0 , 0.0],
    [-pi/2, 0.0, -pi/2 , 0.0]]

LEFT_ARM_MDH_PARAMS = [[-pi/2,0.0,0.0,0.0],
    [ pi/2,0.0,pi/2,0.0],
    [ pi/2,0.0,0.0,UPPER_ARM_LENGTH],
    [-pi/2,0.0,0.0,0.0]]

LEFT_LEG_MDH_PARAMS = [[ -3*pi/4, 0.0,  -pi/2, 0.0],
    [ -pi/2,   0.0,   pi/4, 0.0],
    [ pi/2,    0.0,     0.0, 0.0],
#[ pi/2,-THIGH_LENGTH,0.0, 0.0],
    [   0.0,-THIGH_LENGTH,0.0, 0.0],
    [   0.0,-TIBIA_LENGTH,0.0, 0.0],
    [-pi/2,    0.0,     0.0, 0.0]]

RIGHT_LEG_MDH_PARAMS= [[ -pi/4,  0.0,   -pi/2, 0.0],
    [ -pi/2,   0.0,  -pi/4, 0.0],
    [  pi/2,    0.0,    0.0, 0.0],
#[  pi/2,-THIGH_LENGTH,0.0,0.0],
    [ 0.0,-THIGH_LENGTH,0.0, 0.0],
    [0.0,-TIBIA_LENGTH,0.0,0.0],
    [-pi/2,0.0,0.0,0.0]]

RIGHT_ARM_MDH_PARAMS = [[-pi/2, 0.0,0.0,0.0],
    [ pi/2, 0.0,pi/2,0.0],
    [ pi/2, 0.0,0.0,UPPER_ARM_LENGTH],
    [-pi/2, 0.0,0.0,0.0]]

MDH_PARAMS = [
    HEAD_MDH_PARAMS,
    LEFT_ARM_MDH_PARAMS,
    LEFT_LEG_MDH_PARAMS,
    RIGHT_LEG_MDH_PARAMS,
    RIGHT_ARM_MDH_PARAMS
]

#Base transforms to get from body center to beg. of chain
HEAD_BASE_TRANSFORMS = [
    translation4D( 0.0,
        0.0,
        NECK_OFFSET_Z )]

LEFT_ARM_BASE_TRANSFORMS = [
    translation4D( 0.0,
        SHOULDER_OFFSET_Y,
        SHOULDER_OFFSET_Z ) ]

LEFT_LEG_BASE_TRANSFORMS = [
    translation4D( 0.0,
        HIP_OFFSET_Y,
        -HIP_OFFSET_Z ) ]

RIGHT_LEG_BASE_TRANSFORMS = [
    translation4D( 0.0,
        -HIP_OFFSET_Y,
        -HIP_OFFSET_Z ) ]

RIGHT_ARM_BASE_TRANSFORMS = [
    translation4D( 0.0,
        -SHOULDER_OFFSET_Y,
        SHOULDER_OFFSET_Z ) ]

BASE_TRANSFORMS = [
    HEAD_BASE_TRANSFORMS,
    LEFT_ARM_BASE_TRANSFORMS,
    LEFT_LEG_BASE_TRANSFORMS,
    RIGHT_LEG_BASE_TRANSFORMS,
    RIGHT_ARM_BASE_TRANSFORMS ]

#Base transforms to get from body center to beg. of chain
HEAD_END_TRANSFORMS = [
    rotation4D(X_AXIS, pi/2),
    rotation4D(Y_AXIS, pi/2),
    translation4D(CAMERA_OFF_X, 0, CAMERA_OFF_Z),
    rotation4D(Y_AXIS, CAMERA_PITCH_ANGLE) ]

LEFT_ARM_END_TRANSFORMS = [
    rotation4D(Z_AXIS, -pi/2),
    translation4D(LOWER_ARM_LENGTH,0.0,0.0) ]

LEFT_LEG_END_TRANSFORMS = [
    rotation4D(Z_AXIS, pi),
    rotation4D(Y_AXIS, -pi/2),
    translation4D(0.0,
                  0.0,
                  -FOOT_HEIGHT) ]

RIGHT_LEG_END_TRANSFORMS = [
    rotation4D(Z_AXIS, pi),
    rotation4D(Y_AXIS, -pi/2),
    translation4D(0.0,
                  0.0,
                  -FOOT_HEIGHT) ]

RIGHT_ARM_END_TRANSFORMS = [
    rotation4D(Z_AXIS, -pi/2),
    translation4D(LOWER_ARM_LENGTH,0.0,0.0) ]


END_TRANSFORMS = [
    HEAD_END_TRANSFORMS,
    LEFT_ARM_END_TRANSFORMS,
    LEFT_LEG_END_TRANSFORMS,
    RIGHT_LEG_END_TRANSFORMS,
    RIGHT_ARM_END_TRANSFORMS ]

NUM_BASE_TRANSFORMS = [1,1,1,1,1]
NUM_END_TRANSFORMS = [4,2,3,3,2]
NUM_JOINTS_CHAIN = [2,4,6,6,4]

######

pose = NaoPose()


