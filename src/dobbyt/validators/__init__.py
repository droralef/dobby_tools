"""

Dobby tools - validators package

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

"""

import enum

import dobbyt._utils as _u
from dobbyt import _Dobby_Object

ValidationAxis = enum.Enum('ValidationAxis', 'x y xy')


#-------------------------------------------------------------------
class _BaseValidator(_Dobby_Object):
    """
    Base class for validators
    """

    def __init__(self, enabled=False):
        super(_BaseValidator, self).__init__()
        self.enabled = enabled


    @property
    def enabled(self):
        """Whether the validator is currently enabled (boolean)"""
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        _u.validate_attr_type(self, "enabled", value, bool)
        self._enabled = value


from _ValidationFailed import ValidationFailed

from _GlobalSpeedValidator import GlobalSpeedValidator
from _InstantaneousSpeedValidator import InstantaneousSpeedValidator
from _LocationsValidator import LocationsValidator
from _MovementAngleValidator import MovementAngleValidator
from _MoveByGradientValidator import MoveByGradientValidator

