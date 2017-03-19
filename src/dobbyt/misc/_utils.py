"""

Dobby tools - movement package - private utilities

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from enum import Enum
import numbers

import dobbyt


#--------------------------------------------------------------------------
class ErrMsg(object):

    _invalid_attr_type = "dobbyt error: invalid attempt to set {0}.{1} to a non-{2} value ({3})"
    _set_to_non_positive = "dobbyt error: invalid attempt to set {0}.{1} to a non-positive value ({2})"
    _set_to_negative = "dobbyt error: invalid attempt to set {0}.{1} to a negative value ({2})"
    _set_to_invalid_value = "dobbyt error: {0}.{1} was set to an invalid value ({2})"

    @staticmethod
    def attr_invalid_type(class_name, attr_name, expected_type, arg_value):
        return "dobbyt error: {0}.{1} was set to a non-{2} value ({3})".format(class_name, attr_name, expected_type, arg_value)

    @staticmethod
    def attr_non_positive(class_name, attr_name, arg_value):
        "dobbyt error: {0}.{1} was set to a non-positive value ({2})".format(class_name, attr_name, arg_value)

    @staticmethod
    def attr_negative(class_name, attr_name, arg_value):
        "dobbyt error: {0}.{1} was set to a negative value ({2})".format(class_name, attr_name, arg_value)

    @staticmethod
    def attr_invalid_value(class_name, attr_name, arg_value):
        "dobbyt error: {0}.{1} was set to an invalid value ({2})".format(class_name, attr_name, arg_value)

    #-----------------

    @staticmethod
    def invalid_func_arg_type(method_name, expected_type, arg_name, arg_value):
        return "dobbyt error: {0}() was called with a non-{1} {2} ({3})".format(method_name, expected_type, arg_name, arg_value)

    @staticmethod
    def invalid_method_arg_type(class_name, method_name, expected_type, arg_name, arg_value):
        return "dobbyt error: {0}.{1}() was called with a non-{2} {3} ({4})".format(class_name, method_name, expected_type, arg_name, arg_value)




#--------------------------------------------------------------------------
#
# Base class for validators - contains various implementation issues
#
class BaseValidator(dobbyt._Dobby_Object):

    NoneValues = Enum("NoneValues", "Invalid Valid ChangeTo0")

    def __init__(self, enabled=False):
        super(BaseValidator, self).__init__()
        self.enabled = enabled

    #-----------------------------------------------------------------------------------
    @property
    def enabled(self):
        """Whether the validator is currently enabled (boolean)"""
        return self._enabled

    @enabled.setter
    def enabled(self, value):

        if not isinstance(value, bool):
            raise ValueError(ErrMsg.attr_invalid_type(self.__class__, "enabled", bool, value))

        self._enabled = value

    #============================================================================
    #   Validate attributes
    #============================================================================

    #--------------------------------------
    def validate_type(self, attr_name, value, attr_type, none_allowed=False):
        if value is None:
            if not none_allowed:
                raise ValueError(ErrMsg.attr_invalid_type(type(self), attr_name, attr_type, "None"))
        elif not isinstance(value, attr_type):
            raise ValueError(ErrMsg.attr_invalid_type(type(self), attr_name, attr_type, value))

    #--------------------------------------
    def validate_numeric(self, attr_name, value, none_value=NoneValues.Invalid):
        if value is None:
            if none_value == BaseValidator.NoneValues.Invalid:
                raise ValueError(ErrMsg.attr_invalid_type(type(self), attr_name, "numeric", "None"))
            elif none_value == BaseValidator.NoneValues.Valid:
                pass
            elif none_value == BaseValidator.NoneValues.ChangeTo0:
                value = 0

        if value is not None and not isinstance(value, numbers.Number):
            raise ValueError(ErrMsg.attr_invalid_type(type(self), attr_name, "numeric", value))

        return value

    #--------------------------------------
    def validate_not_negative(self, attr_name, value):
        if value is not None and value < 0:
            raise ValueError(ErrMsg.attr_negative(type(self), attr_name, value))

    #--------------------------------------
    def validate_positive(self, attr_name, value):
        if value is not None and value <= 0:
            raise ValueError(ErrMsg.attr_non_positive(type(self), attr_name, value))


    #============================================================================
    #   Other validations
    #============================================================================

    #--------------------------------------
    def mouse_at_validate_xy(self, x_coord, y_coord):
        #-- Validate types
        if not isinstance(x_coord, numbers.Number):
            raise ValueError(ErrMsg.invalid_method_arg_type(type(self), "mouse_at", "numeric", "x_coord", x_coord))
        if not isinstance(y_coord, numbers.Number):
            raise ValueError(ErrMsg.invalid_method_arg_type(type(self), "mouse_at", "numeric", "y_coord", y_coord))


    #--------------------------------------
    def mouse_at_validate_xyt(self, x_coord, y_coord, time):
        #-- Validate types
        self.mouse_at_validate_xy(x_coord, y_coord)
        if not isinstance(time, numbers.Number):
            raise ValueError(ErrMsg.invalid_method_arg_type(type(self), "mouse_at", "numeric", "time", time))

