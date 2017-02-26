"""

Local speed validator: Validate minimal/maximal instantaneous speed

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numbers
from enum import Enum

import dobbyt


class InstantaneousSpeedValidator(dobbyt._Dobby_Object):
    """
    Validator for momentary (instantanesous) speed: make sure that at each given moment, the
    movement speed is within the valid boundaries

    The min/max speed are configured as mm/sec, but the movement progress is provided in arbitrary units
    (e.g., pixels). You'll therefore need to define the units-per-mm ratio.
    """

    Axis = Enum('Axis', 'x y xy')

    #-----------------------------------------------------------------------------------
    def __init__(self, units_per_mm, axis=Axis.y, enabled=False, min_speed=None, max_speed=None, grace_period=0):
        """
        Constructor
        :param units_per_mm: The ratio of units (provided in the call to XXX) per mm
        :param axis: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.axis`
        :param enabled: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.enabled`
        :param min_speed: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.min_speed`
        :param max_speed: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.max_speed`
        :param grace_period: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.grace_period`
        """
        #TODO: fix comment above

        super(InstantaneousSpeedValidator, self).__init__()

        if not isinstance(units_per_mm, numbers.Number):
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_numeric.format("units_per_mm", units_per_mm))

        self._units_per_mm = units_per_mm

        self.enabled = enabled
        self.axis = axis
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.grace_period = grace_period


    #========================================================================
    #      Config
    #========================================================================

    _errmsg_set_to_non_numeric = "dobbyt error: invalid attempt to set InstantaneousSpeedValidator.{0} to a non-numeric value ({1})"
    _errmsg_set_to_non_positive = "dobbyt error: invalid attempt to set InstantaneousSpeedValidator.{0} to a non-positive value ({1})"
    _errmsg_set_to_negative = "dobbyt error: invalid attempt to set InstantaneousSpeedValidator.{0} to a negative value ({1})"
    _errmsg_set_to_non_boolean = "dobbyt error: invalid attempt to set InstantaneousSpeedValidator.{0} to a non-boolean value ({1})"

    #-----------------------------------------------------------------------------------
    @property
    def enabled(self):
        """Whether the validator is currently enabled"""
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        """
        Determine whether the validator is currently enabled
        :param value: Boolean
        """

        if not isinstance(value, bool):
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_boolean.format("enabled", value))

        self._enabled = value

    #-----------------------------------------------------------------------------------
    @property
    def axis(self):
        """Get the axis on which speed is validated (type = InstantaneousSpeedValidator.Axis)"""
        return self._axis

    @axis.setter
    def axis(self, value):
        """
        Set the axis on which speed is validated
        :param value: an enum of type InstantaneousSpeedValidator.Axis.
                      Axis.x or Axis.y: limit the speed in the relevant axis.
                      Axis.xy: limit the diagonal speed
        """

        if not isinstance(value, InstantaneousSpeedValidator.Axis):
            raise AttributeError("dobbyt error: invalid value ({0}) for InstantaneousSpeedValidator.axis - expecting a value of type InstantaneousSpeedValidator.Axis".format(value))

        self._axis = value

    #-----------------------------------------------------------------------------------
    @property
    def min_speed(self):
        """The minimal valid instantaneous speed (mm/sec)"""
        return self._min_speed

    @min_speed.setter
    def min_speed(self, value):
        """
        The minimal speed set by this validator
        :param value: The speed (mm/sec) - must be a positive value. "None" means that minimal speed will not be enforced.
        """

        if value is not None:
            if not isinstance(value, numbers.Number):
                raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_numeric.format("min_speed", value))
            if not value <= 0:
                raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_positive.format("min_speed", value))

        self._min_speed = value

    #-----------------------------------------------------------------------------------
    @property
    def max_speed(self):
        """The maximal valid instantaneous speed (mm/sec)"""
        return self._max_speed

    @max_speed.setter
    def max_speed(self, value):
        """
        The maximal speed set by this validator
        :param value: The speed (mm/sec) - must be a positive value. "None" means that minimal speed will not be enforced.
        """

        if value is not None:
            if not isinstance(value, numbers.Number):
                raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_numeric.format("max_speed", value))
            if not value <= 0:
                raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_positive.format("max_speed", value))

        self._max_speed = value

    #-----------------------------------------------------------------------------------
    @property
    def grace_period(self):
        """Get the grace period in the beginning of each trial, during which speed is not validated"""
        return self._grace_period

    @grace_period.setter
    def grace_period(self, value):
        """
        Get the grace period in the beginning of each trial, during which speed is not validated
        :param value: The period (in seconds). Only values >= 0 are valid.
        """

        if value is None:
            value = 0

        if not isinstance(value, numbers.Number):
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_numeric.format("grace_period", value))
        if not value < 0:
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_positive.format("grace_period", value))

        self._grace_period = value
