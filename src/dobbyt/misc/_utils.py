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

NoneValues = Enum("NoneValues", "Invalid Valid ChangeTo0")


#--------------------------------------
def _get_type_name(t):
    if isinstance(t, (list, tuple)):
        return "/".join([_get_type_name(tt) for tt in t])
    if t == numbers.Number:
        return "number"
    else:
        return str(t)


#--------------------------------------
def validate_attr_type(obj, attr_name, value, attr_type, none_allowed=False, type_name=None):

    if (value is None and not none_allowed) or (value is not None and not isinstance(value, attr_type)):
        if type_name is None:
            type_name = _get_type_name(attr_type)

        raise ValueError(ErrMsg.attr_invalid_type(type(obj), attr_name, type_name, value))


#--------------------------------------
def validate_attr_numeric(obj, attr_name, value, none_value=NoneValues.Invalid):
    if value is None:
        if none_value == NoneValues.Invalid:
            raise ValueError(ErrMsg.attr_invalid_type(type(obj), attr_name, "numeric", "None"))
        elif none_value == NoneValues.Valid:
            pass
        elif none_value == NoneValues.ChangeTo0:
            value = 0

    if value is not None and not isinstance(value, numbers.Number):
        raise ValueError(ErrMsg.attr_invalid_type(type(obj), attr_name, "numeric", value))

    return value

#--------------------------------------
def validate_attr_not_negative(obj, attr_name, value):
    if value is not None and value < 0:
        raise ValueError(ErrMsg.attr_negative(type(obj), attr_name, value))

#--------------------------------------
def validate_attr_positive(obj, attr_name, value):
    if value is not None and value <= 0:
        raise ValueError(ErrMsg.attr_non_positive(type(obj), attr_name, value))


#============================================================================
#   Validate function arguments
#============================================================================

#-------------------------------------------------------------------------
def validate_func_arg_type(obj, func_name, arg_name, value, arg_type, none_allowed=False, type_name=None):

    if (value is None and not none_allowed) or (value is not None and not isinstance(value, arg_type)):
        if type_name is None:
            type_name = _get_type_name(arg_type)

        if obj is None:
            raise ValueError(ErrMsg.invalid_func_arg_type(func_name, type_name, arg_name, value))
        else:
            raise ValueError(ErrMsg.invalid_method_arg_type(type(obj), func_name, type_name, arg_name, value))



