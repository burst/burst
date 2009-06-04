"""
Position computations out of various landmarks


MAJOR TODO: Testing. This is pure math code, it should
be tested, and also carefully checked for input conditions
"""

from math import atan2, asin, sin, cos
from burst_util import close_to_zero

def xyt_from_two_dist_one_angle(r1, r2, a1, d, p0, p1, debug=False):
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

def kick_angle_size_from_distance_and_angle_to_mid_target(r, a, l):
    """
    r - distance to center of target (i.e. goal)
    a - angle of target (i.e. total angle goal takes, or difference
        of bearing to right and to left post when they are centered - two
        strategies to compute a)
    l - distance from target middle to both ends (i.e. half goal width)

    returns +-b, the kick angle, from which x and y are computed so: (in center
    of target coordinate system)
    
    on sign of b: we cannot compute the sign of b since there is a symmetry to
    the problem. To break this we must have r1 and r2 and know which is larger.
    That is left for the caller.

    x = cos(b) * r
    y = sin(b) * r
    """
    d = r**2
    e = l**2
    f = cos(a)**2
    if close_to_zero(f): return None # infinite solutions - you are on the circle
                                     # you must rely on r1, r2
    sin_b_2 = ( (d+e)**2 - (d-e)**2 / f ) / (4*d*e)
    return asin(sin_b_2**0.5)
