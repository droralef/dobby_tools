"""

  Validator for minimal/maximal instantaneous speed

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import numbers

import numpy as np

import dobbyt
from dobbyt.misc._utils import BaseValidator, ErrMsg
from dobbyt.validators import ValidationAxis, ValidationFailed
from dobbyt.movement import InstMovementMonitor


# noinspection PyAttributeOutsideInit
class InstantaneousSpeedValidator(BaseValidator):
    """
    Validator for momentary (instantanesous) speed: make sure that at each given moment, the
    movement speed is within the valid boundaries

    The min/max speed are configured as mm/sec, but the movement progress is provided in arbitrary units
    (e.g., pixels). You'll therefore need to define the units-per-mm ratio.
    """

    err_too_slow = "too_slow"
    err_too_fast = "too_fast"
    arg_speed = 'speed'  # ValidationFailed exception argument: the speed observed

    #-----------------------------------------------------------------------------------
    def __init__(self, units_per_mm, axis=ValidationAxis.y, enabled=False, min_speed=None, max_speed=None,
                 grace_period=0, calculation_interval=0, movement_monitor=None):
        """
        Constructor
        :param units_per_mm: The ratio of units (provided in the call to :func:`~dobbyt.movement.InstantaneousSpeedValidator.mouse_at`) per mm
        :param axis: See :func:`~dobbyt.movement.ValidationAxis`
        :param enabled: See :func:`~dobbyt.validators.InstantaneousSpeedValidator.enabled`
        :param min_speed: See :func:`~dobbyt.validators.InstantaneousSpeedValidator.min_speed`
        :param max_speed: See :func:`~dobbyt.validators.InstantaneousSpeedValidator.max_speed`
        :param grace_period: See :func:`~dobbyt.validators.InstantaneousSpeedValidator.grace_period`
        :param calculation_interval: See :func:`~dobbyt.validators.InstantaneousSpeedValidator.calc_speed_interval`
        """

        super(InstantaneousSpeedValidator, self).__init__(enabled=enabled)

        if not isinstance(units_per_mm, numbers.Number):
            raise ValueError(ErrMsg.attr_invalid_type(self.__class__, "units_per_mm", "numeric", units_per_mm))

        if movement_monitor is None:
            self._movement_monitor = InstMovementMonitor(units_per_mm, calculation_interval)
        elif isinstance(movement_monitor, InstMovementMonitor):
            self._movement_monitor = movement_monitor
        else:
            raise ValueError(ErrMsg.invalid_method_arg_type(self.__class__, "__init__", "movement_monitor", "InstMovementMonitor", movement_monitor))

        self.axis = axis
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.grace_period = grace_period
        self.calculation_interval = calculation_interval

        self.reset()


    #========================================================================
    #      Validation API
    #========================================================================


    #-----------------------------------------------------------------------------------
    def reset(self, time=None):
        """
        Called when a trial starts - reset any previous movement
        :param time: The time when the trial starts. The grace period will be determined according to this time.
        """
        self._movement_monitor.reset(time)


    #-----------------------------------------------------------------------------------
    def mouse_at(self, x_coord, y_coord, time):
        """
        Given a current position, check whether the movement complies with the speed limits.
        :param x_coord: Current x coordinate (in the predefined coordinate system)
        :param y_coord: Current y coordinate (in the predefined coordinate system)
        :param time: Time, in seconds. The zero point doesn't matter, as long as you're consistent until reset() is called.
        :return: True if there was an error.
        """

        if not self._enabled:
            return

        self._movement_monitor.mouse_at(x_coord, y_coord, time)


        #-- Calculate speed, if possible
        if self._movement_monitor.time_in_trial is not None and \
            self._movement_monitor.time_in_trial > self._grace_period and \
            self._movement_monitor.last_calculation_interval is not None:

            if self._axis == ValidationAxis.x:
                speed = self._movement_monitor.xspeed
            elif self._axis == ValidationAxis.y:
                speed = self._movement_monitor.yspeed
            elif self._axis == ValidationAxis.xy:
                speed = self._movement_monitor.xyspeed
            else:
                return

            if self._min_speed is not None and speed < self._min_speed:
                raise ValidationFailed(self.err_too_slow, "You moved too slowly", self, { self.arg_speed : speed })

            if self._max_speed is not None and speed > self._max_speed:
                raise ValidationFailed(self.err_too_fast, "You moved too fast", self, { self.arg_speed : speed })


    #--------------------------------------
    def _mouse_at_validate_time(self, time):

        #-- Validate that times are provided in increasing order
        prev_time = self._prev_locations[-1][2] if len(self._prev_locations) > 0 else self._time0
        if len(self._prev_locations) > 0 and prev_time > time:
            raise dobbyt.InvalidStateError("{0}.mouse_at() was called with time={1} after it was previously called with time={2}".format(self.__class__, time, prev_time))


    #--------------------------------------
    # Remove the oldest previous locations, but make sure that self._prev_locations[0] remains
    # old enough to be usable for speed computation
    #
    def _remove_too_old_prev_locations(self, latest_good_time):
        older_than_threshold = np.where([p[2] <= latest_good_time for p in self._prev_locations])
        older_than_threshold = older_than_threshold[0]
        if len(older_than_threshold) > 1:
            self._prev_locations = self._prev_locations[older_than_threshold[-1]:]

    #--------------------------------------
    @staticmethod
    def _calc_speed_x(xyt1, xyt2):
        dx = xyt2[0] - xyt1[0]
        dt = xyt2[2] - xyt1[2]
        return dx / dt

    @staticmethod
    def _calc_speed_y(xyt1, xyt2):
        dy = xyt2[1] - xyt1[1]
        dt = xyt2[2] - xyt1[2]
        return dy / dt

    @staticmethod
    def _calc_speed_xy(xyt1, xyt2):
        dx = xyt2[0] - xyt1[0]
        dy = xyt2[1] - xyt1[1]
        dt = xyt2[2] - xyt1[2]
        return np.sqrt(dx**2 + dy**2) / dt


    #========================================================================
    #      Config
    #========================================================================

    #-----------------------------------------------------------------------------------
    @property
    def axis(self):
        """
        The ValidationAxis on which speed is validated
        ValidationAxis.x or ValidationAxis.y: limit the speed in the relevant axis.
        ValidationAxis.xy: limit the diagonal speed
        """
        return self._axis

    @axis.setter
    def axis(self, value):
        self.validate_type("axis", value, ValidationAxis)
        self._axis = value


    #-----------------------------------------------------------------------------------
    @property
    def min_speed(self):
        """
        The minimal valid instantaneous speed (mm/sec).
        Only positive values are valid. None = minimal speed will not be enforced.
        """
        return self._min_speed

    @min_speed.setter
    def min_speed(self, value):
        self.validate_numeric("min_speed", value, none_value=BaseValidator.NoneValues.Valid)
        self.validate_positive("min_speed", value)
        self._min_speed = value

    #-----------------------------------------------------------------------------------
    @property
    def max_speed(self):
        """
        The maximal valid instantaneous speed (mm/sec).
        Only positive values are valid. None = maximal speed will not be enforced.
        """
        return self._max_speed

    @max_speed.setter
    def max_speed(self, value):
        self.validate_numeric("max_speed", value, none_value=BaseValidator.NoneValues.Valid)
        self.validate_positive("max_speed", value)
        self._max_speed = value

    #-----------------------------------------------------------------------------------
    @property
    def grace_period(self):
        """The grace period in the beginning of each trial, during which speed is not validated (in seconds)."""
        return self._grace_period

    @grace_period.setter
    def grace_period(self, value):
        value = self.validate_numeric("grace_period", value, none_value=BaseValidator.NoneValues.ChangeTo0)
        self.validate_not_negative("grace_period", value)
        self._grace_period = value

    #-----------------------------------------------------------------------------------
    @property
    def calculation_interval(self):
        """
        Time interval (in seconds) for testing speed: the speed is calculated according to the difference in
        (x,y) coordinates over a time interval at least this long.
        """
        return self._movement_monitor.calculation_interval

    @calculation_interval.setter
    def calculation_interval(self, value):
        self._movement_monitor.calculation_interval = value
