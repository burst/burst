import math
import time
from motion_CurrentConfig import *

####
# Create python broker

try:
    broker = ALBroker("pythonBroker","127.0.0.1",6665,IP, PORT)
except RuntimeError,e:
    print("cannot connect")
    exit(1)

####
# Create motion proxy

print "Creating motion proxy"


try:
    motionProxy = ALProxy("ALMotion")
except Exception,e:
    print "Error when creating motion proxy:"
    print str(e)
    exit(1)

####
# Motion Config

initial_angles = [-4.196167e-05, -4.196167e-05, 1.7453624000000001, 0.26179266000000001, -1.5707622000000001, -0.52362728000000003, -4.196167e-05, 0.0, 0.0033975868, -0.051347039999999997, -0.45210454, 0.80281532, -0.40540146999999999, 0.051335089, 0.0033975868, 0.035707463000000002, -0.45391422999999997, 0.80587136999999998, -0.40675569, -0.035815290999999999, 1.7453505, -0.26178071000000003, 1.5707741, 0.52361535999999997, -4.196167e-05, 0.0]

def set_angles_to_walk_start():
    print "Settings body angles to start of walk"
    motionProxy.setBodyAngles(initial_angles)
    print "done"

motionProxy.setWalkArmsConfig( 100.0 * motion.TO_RAD, 10.0 * motion.TO_RAD, 30.0 * motion.TO_RAD, 10.0 * motion.TO_RAD )
motionProxy.setWalkArmsEnable(True)
motionProxy.setWalkExtraConfig( 4.5, -4.5, 0.22, 2.0 )
motionProxy.setWalkConfig( 0.05, 0.04, 0.06, 0.4, 0.01, 0.00 )
motionProxy.setBalanceMode(1)
motionProxy.setAngle ('HeadPitch', -30*motion.TO_RAD)
motionProxy.setSupportMode(motion.SUPPORT_MODE_DOUBLE_LEFT)

####
# Movement Class
#
# This class cotrols the logic of choosing the right type of walk
# for the robot.
class Movement(object):
    x1= 0
    y1= 0
    yaw1= 0
    x2= 0
    y2= 0
    yaw2= 0
    steps= 25
    ####
    # __init__()
    # Input:      Intial position (x,y,yaw) and final position (x,y,yaw)
    #             notes: The yaw is in degrees.
    #                    (-x,-y) -> First quadrant.
    #                    (-x,y) -> Second quadrant.
    #                    (x,y) -> Third quadrant.
    #                    (x,-y) -> Fourth quadrant.
    # Output:     -
    # Operation:  Initialize both positions of the robots.
    def __init__(self, x1, y1, yaw1, x2, y2, yaw2):
        Movement.x1= x1
        Movement.y1= y1
        Movement.yaw1= yaw1
        Movement.x2= x2
        Movement.y2= y2
        Movement.yaw2= yaw2
    ####
    # normalize()
    # Input:      -
    # Output:     -
    # Operation:  Normalize the positions to be relative to the robot's
    #             initial position, thus the robot's initial position will
    #             be (0,0,0).
    def normalize(self):
        if Movement.x1!=0 or Movement.y1!=0:
            # Subtract initial position x-axis value from the final position x-axis value.
            Movement.x2= Movement.x2 - Movement.x1
            # Subtract initial position y-axis value from the final position y-axis value.
            Movement.y2= Movement.y2 - Movement.y1
            # Initial x-axis value is 0.
            Movement.x1= 0
            # Initial y-axis value is 0.
            Movement.y1= 0
            # Subtract initial yaw value from the final yaw value.
            Movement.yaw2= Movement.yaw2 - Movement.yaw1
            # Initial yaw value is 0.
            Movement.yaw1= 0
    ####
    # strafe()
    # Input:      Final x, y and yaw.
    # Output:     -
    # Operation:  Turns the robot to a position which is perpendicular
    # to the azimuth of the final destination, then walks sideways and finally corrects its
    # angle to match the final yaw.
    def strafe(self, x, y, yaw):
        # Distance d = square_root(y^2 + x^2)
        dist= math.sqrt(y.__pow__(2)+x.__pow__(2))
        # The angle between the robot's current yaw and the azimuth of the final destination.
        # angle = arctan(x/y)
        angle= (math.atan(math.fabs(x)/math.fabs(y))*180)/math.pi
        # The second and fourth quadrants require the robot to turn with a negative angle (turn right).
        if (y*x)<0:
            angle= -angle
        # The first and fourth quadrants require the robot to move with negative distance (move right).
        if y<0:
            dist= -dist
        # Turn with angle.
        self.turn(angle)
        # Walk sideways with dist.
        motionProxy.addWalkSideways(dist,Movement.steps)
        # Subtract the angle that the robot already made from the destination yaw.
        diffangle= yaw - angle
        # Create the compliment angle.
        # The robot will then choose the minimal angle to turn in order to position itself
        # as was requested.
        if diffangle>0:
            # Compliment of a positive angle is the angle - 360.
            odiffangle= diffangle - 360
        else:
            # Compliment of a negative angle is the angle + 360.
            odiffangle= diffangle + 360
        # Choose the minimal angle.
        if(math.fabs(odiffangle)>math.fabs(diffangle)):
            # Turn with angle.
            self.turn(diffangle)
        else:
            # Turn with angle.
            self.turn(odiffangle)
        # Commit the plan.
        motionProxy.walk()
    ####
    # arc()
    # Input:      Final x, y and yaw.
    # Output:     -
    # Operation:  The initial point and destination point positioned on a circle, create an arc.
    #             The robot walks the arc, and then turns to position itself according to the final yaw.
    def arc(self, x, y, yaw):
        # Distance d = square_root(y^2 + x^2)
        dist= math.sqrt(y.__pow__(2)+x.__pow__(2))
        # The angle between the robot's current yaw and the azimuth of the final destination.
        # angle = arctan(x/y)
        angle= (math.atan(math.fabs(x)/math.fabs(y))*180)/math.pi
        # When the robot has to reach a point in the third of fourth quadrand,
        # it should first turn 90 degrees to the left / right, making the point within
        # its arc range (which is 180 degrees).
        turn90angle= 0
        # The point is in the third or fourth quadrants.
        if x>0:
            # The angle which the robot has to take after the 90-degrees turn,
            # is arctan(y/x) = 90 - arctan(x/y). ( The axis 90-degrees as well ).
            angle= 90 - angle
            # If the point is within the first or fourth quadrants, the robot has to turn
            # with a negative angle ( turn 90-degrees right ).
            if y<0:
                turn90angle= -90
            # Else, 90 degrees left.
            else:
                turn90angle= 90
            # Turn 90-degrees.
            self.turn(turn90angle)
        # The angle of the arc is negative when the point is within the first or fourth quadrants.
        # ( Move + Turn right ).
        if y<0:
            # The two points and the circle's center create an isosceles triangle inside the circle ( the sides are the
            # circle's radius ), when the angle is actually on the the base angles of the triangle and the central angle
            # equals to: Central angle = 180 - 2 * angle.
            central_angle= -(180-2*angle)
        # Else, it's positive. ( Move + Turn left ).
        else:
            central_angle= 180-2*angle
        # Radius r = d / ( 2 * sin( 90 - angle ) ). According to the law of sines.
        radius= dist/(2*math.cos((angle)*motion.TO_RAD))
        # Walk in arc with
        motionProxy.addWalkArc(central_angle*motion.TO_RAD, radius, Movement.steps)
        #
        diffangle= yaw - central_angle - turn90angle
        if diffangle>0:
            odiffangle= diffangle - 360
        else:
            odiffangle= diffangle + 360
        if(math.fabs(odiffangle)>math.fabs(diffangle)):
            self.turn(diffangle)
        else:
            self.turn(odiffangle)
        motionProxy.walk()
    def straight(self, x, y, yaw):
        dist= math.sqrt(y.__pow__(2)+x.__pow__(2))
        if y == 0:
            angle= 0
            if x>0:
                dist= -dist
        else:
            angle= (math.atan(math.fabs(x)/math.fabs(y))*180)/math.pi
            if x>0:
                angle= angle + 90
            else:
                angle= 90 - angle
            if y<0:
                angle= -angle
        self.turn(angle)
        motionProxy.addWalkStraight(dist,Movement.steps)
        diffangle= yaw - angle
        if diffangle>0:
            odiffangle= diffangle - 360
        else:
            odiffangle= diffangle + 360
        if(math.fabs(odiffangle)>math.fabs(diffangle)):
            self.turn(diffangle)
        else:
            self.turn(odiffangle)
        motionProxy.walk()

    def turn(self, yaw):
        motionProxy.addTurn(yaw*motion.TO_RAD,Movement.steps)
        motionProxy.walk()

    def run(self):
        set_angles_to_walk_start()
        before_t= time.time()
        self.normalize()
        self.straight(Movement.x2,Movement.y2, Movement.yaw2)
        after_t= time.time()
        time1= after_t-before_t
        time.sleep(18)
        before_t= time.time()
        self.arc(Movement.x2,Movement.y2, Movement.yaw2)
        after_t= time.time()
        time2= after_t-before_t
        time.sleep(18)
        before_t= time.time()
        self.strafe(Movement.x2,Movement.y2, Movement.yaw2)
        after_t= time.time()
        time3= after_t-before_t
        time.sleep(18)
        return [time1, time2, time3]

