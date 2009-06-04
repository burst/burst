"""
Utilities that rely on the heavy (to load mainly) numpy and scipy libraries.
The idea is to assure the user that numpy loading happens only when loading
this libarary. Also a single point to worry about compatibility.
"""

import numpy
from numpy import (sin, cos, zeros,
    tan, array, dot)
from numpy.linalg import norm
from scipy.linalg import lu, lu_factor

from burst_consts import X_AXIS, Y_AXIS, Z_AXIS, W_AXIS

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


