"""

Dobby tools - movement package - utilities

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from numpy import pi, arctan
from enum import Enum
import numbers

import dobbyt

#--------------------------------------------------------------------------
def get_angle(xy1, xy2):
    """
    Get the direction of finger movement, in radians. 0 = upwards.
    :param xy1: Coordinates in time point #1
    :param xy2: Coordinates in a later time point
    """

    dx = xy2[0] - xy1[0]
    dy = xy2[1] - xy1[1]

    if dx == 0:
        # up=0, down=pi
        return 0 if dy > 0 else pi
    elif dx > 0:
        # Right movement; return angles from 0 to pi
        angle = arctan(- dy / dx) + pi / 2
    else:
        # Left movement; return angles from pi to pi*2
        angle = arctan(- dy / dx) + pi * 3 / 2

    return angle


#--------------------------------------------------------------------------
#
# Base class for validators - contains various implementation issues
#
class BaseValidator(dobbyt._Dobby_Object):

    NoneValues = Enum("NoneValues", "Invalid Valid ChangeTo0")

    _errmsg_set_to_invalid_type = "dobbyt error: invalid attempt to set {0}.{1} to a non-{2} value ({3})"
    _errmsg_set_to_non_positive = "dobbyt error: invalid attempt to set {0}.{1} to a non-positive value ({2})"
    _errmsg_set_to_negative = "dobbyt error: invalid attempt to set {0}.{1} to a negative value ({2})"
    _errmsg_set_to_invalid_value = "dobbyt error: {0}.{1} was set to an invalid value ({2})"

    _errmsg_non_numeric_func_arg = "dobbyt error: {0}.{1}() was called with a non-numeric {2} ({3})"

    #--------------------------------------
    def mouse_at_validate_xyt(self, x_coord, y_coord, time):
        #-- Validate types
        if not isinstance(x_coord, numbers.Number):
            raise AttributeError(BaseValidator._errmsg_non_numeric_func_arg.format(type(self), "x_coord", x_coord))

        if not isinstance(y_coord, numbers.Number):
            raise AttributeError(BaseValidator._errmsg_non_numeric_func_arg.format(type(self), "y_coord", y_coord))

        if not isinstance(time, numbers.Number):
            raise AttributeError(BaseValidator._errmsg_non_numeric_func_arg.format(type(self), "time", time))

    #============================================================================
    #   Validate attributes
    #============================================================================

    #--------------------------------------
    def validate_type(self, attr_name, value, attr_type, none_allowed=False):
        if value is None:
            if not none_allowed:
                raise AttributeError(BaseValidator._errmsg_set_to_invalid_type.format(type(self), attr_name, attr_type, "None"))
        elif not isinstance(value, attr_type):
            raise AttributeError(BaseValidator._errmsg_set_to_invalid_type.format(type(self), attr_name, attr_type, value))

    #--------------------------------------
    def validate_numeric(self, attr_name, value, none_value=NoneValues.Invalid):
        if value is None:
            if none_value == BaseValidator.NoneValues.Invalid:
                raise AttributeError(BaseValidator._errmsg_set_to_invalid_type.format(type(self), attr_name, "numeric", "None"))
            elif none_value == BaseValidator.NoneValues.Valid:
                pass
            elif none_value == BaseValidator.NoneValues.ChangeTo0:
                value = 0

        if value is not None and not isinstance(value, numbers.Number):
            raise AttributeError(BaseValidator._errmsg_set_to_invalid_type.format(type(self), attr_name, "numeric", value))

        return value

    #--------------------------------------
    def validate_not_negative(self, attr_name, value):
        if value is not None and value < 0:
            raise AttributeError(BaseValidator._errmsg_set_to_negative.format(type(self), attr_name, value))

    #--------------------------------------
    def validate_positive(self, attr_name, value):
        if value is not None and value <= 0:
            raise AttributeError(BaseValidator._errmsg_set_to_non_positive.format(type(self), attr_name, value))

