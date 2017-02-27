"""

  Validator for minimal/maximal instantaneous speed

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import numpy as np
import numbers

import dobbyt
from dobbyt.movement import ValidationAxis, SpeedError


# noinspection PyAttributeOutsideInit
class InstantaneousSpeedValidator(dobbyt._Dobby_Object):
    """
    Validator for momentary (instantanesous) speed: make sure that at each given moment, the
    movement speed is within the valid boundaries

    The min/max speed are configured as mm/sec, but the movement progress is provided in arbitrary units
    (e.g., pixels). You'll therefore need to define the units-per-mm ratio.
    """

    #-----------------------------------------------------------------------------------
    def __init__(self, units_per_mm, axis=ValidationAxis.y, active=False, min_speed=None, max_speed=None,
                 grace_period=0, calc_speed_interval=0):
        """
        Constructor
        :param units_per_mm: The ratio of units (provided in the call to :func:`~dobbyt.movement.InstantaneousSpeedValidator.mouse_at`) per mm
        :param axis: See :func:`~dobbyt.movement.ValidationAxis`
        :param active: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.active`
        :param min_speed: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.min_speed`
        :param max_speed: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.max_speed`
        :param grace_period: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.grace_period`
        :param calc_speed_interval: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.calc_speed_interval`
        """

        super(InstantaneousSpeedValidator, self).__init__()

        if not isinstance(units_per_mm, numbers.Number):
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_numeric.format("units_per_mm", units_per_mm))

        self._units_per_mm = units_per_mm

        self.active = active
        self.axis = axis
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.grace_period = grace_period
        self.calc_speed_interval = calc_speed_interval

        self.reset()


    #========================================================================
    #      Validation API
    #========================================================================

    _errmsg_mouse_at_non_numeric = "dobbyt error: {0}.mouse_at was called with a non-numeric {1} ({2})"

    #-----------------------------------------------------------------------------------
    def reset(self, time=None):
        """
        Called when a trial starts - reset any previous movement
        :param time: The time when the trial starts. The grace period will be determined according to this time.
        """
        if time is not None and not isinstance(time, (int, float)):
            raise AttributeError("dobbyt error: {0}.reset() was called with a non-numeric time".format(type(self), time))

        self._prev_locations = []
        self._time0 = time


    #-----------------------------------------------------------------------------------
    def mouse_at(self, x_coord, y_coord, time):
        """
        Given a current position, check whether the movement complies with the speed limits.
        :param x_coord: Current x coordinate (in the predefined coordinate system)
        :param y_coord: Current y coordinate (in the predefined coordinate system)
        :param time: Time, in seconds. The zero point doesn't matter, as long as you're consistent until reset() is called.
        :return: True if there was an error.
        """

        if not self._active:
            return SpeedError.OK

        self._mouse_at_validate_xyt(x_coord, y_coord, time)

        if self._time0 is None:
            self._time0 = time

        curr_xyt = (x_coord / self._units_per_mm, y_coord / self._units_per_mm, time)

        latest_prev_time = time - self._calc_speed_interval
        self._remove_too_old_prev_locations(latest_prev_time)

        #-- Remember current coords & time
        self._prev_locations.append(curr_xyt)

        #-- Calculate speed, if possible
        if len(self._prev_locations) > 1 \
                and self._prev_locations[0][2] <= latest_prev_time \
                and (self._grace_period is None or time-self._time0 > self._grace_period):

            speed = self._calc_speed_func(self._prev_locations[0], curr_xyt)

            if self._min_speed is not None and speed < self._min_speed:
                return SpeedError.TooSlow

            if self._max_speed is not None and speed > self._max_speed:
                return SpeedError.TooFast

        return SpeedError.OK


    #--------------------------------------
    def _mouse_at_validate_xyt(self, x_coord, y_coord, time):
        #-- Validate types
        if not isinstance(x_coord, numbers.Number):
            raise AttributeError(InstantaneousSpeedValidator._errmsg_mouse_at_non_numeric.format(type(self), "x_coord", x_coord))

        if not isinstance(y_coord, numbers.Number):
            raise AttributeError(InstantaneousSpeedValidator._errmsg_mouse_at_non_numeric.format(type(self), "y_coord", y_coord))

        if not isinstance(time, numbers.Number):
            raise AttributeError(InstantaneousSpeedValidator._errmsg_mouse_at_non_numeric.format(type(self), "time", time))

        #-- Validate that times are provided in increasing order
        prevTime = self._prev_locations[-1][2] if len(self._prev_locations) > 0 else self._time0
        if len(self._prev_locations) > 0 and prevTime > time:
            raise dobbyt.InvalidStateError("{0}.mouse_at() was called with time={1} after it was previously called with time={2}".format(type(self), time, prevTime))


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

    _errmsg_set_to_non_numeric = "dobbyt error: invalid attempt to set {0}.{1} to a non-numeric value ({2})"
    _errmsg_set_to_non_positive = "dobbyt error: invalid attempt to set {0}.{1} to a non-positive value ({2})"
    _errmsg_set_to_negative = "dobbyt error: invalid attempt to set {0}.{1} to a negative value ({2})"
    _errmsg_set_to_non_boolean = "dobbyt error: invalid attempt to set {0}.{1} to a non-boolean value ({2})"

    #-----------------------------------------------------------------------------------
    @property
    def active(self):
        """Whether the validator is currently active (boolean)"""
        return self._active

    @active.setter
    def active(self, value):

        if not isinstance(value, bool):
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_boolean.format(type(self), "active", value))

        self._active = value

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

        if value == ValidationAxis.x:
            self._calc_speed_func = InstantaneousSpeedValidator._calc_speed_x
        elif value == ValidationAxis.y:
            self._calc_speed_func = InstantaneousSpeedValidator._calc_speed_y
        elif value == ValidationAxis.xy:
            self._calc_speed_func = InstantaneousSpeedValidator._calc_speed_xy
        else:
            raise AttributeError("dobbyt error: invalid value ({0}) for InstantaneousSpeedValidator.axis - expecting a value of type ValidationAxis".format(value))

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
        if value is not None:
            if not isinstance(value, numbers.Number):
                raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_numeric.format(type(self), "min_speed", value))
            if value <= 0:
                raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_positive.format(type(self), "min_speed", value))

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
        if value is not None:
            if not isinstance(value, numbers.Number):
                raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_numeric.format(type(self), "max_speed", value))
            if value <= 0:
                raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_positive.format(type(self), "max_speed", value))

        self._max_speed = value

    #-----------------------------------------------------------------------------------
    @property
    def grace_period(self):
        """The grace period in the beginning of each trial, during which speed is not validated (in seconds)."""
        return self._grace_period

    @grace_period.setter
    def grace_period(self, value):
        if value is None:
            value = 0

        if not isinstance(value, numbers.Number):
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_numeric.format(type(self), "grace_period", value))
        if value < 0:
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_negative.format(type(self), "grace_period", value))

        self._grace_period = value

    #-----------------------------------------------------------------------------------
    @property
    def calc_speed_interval(self):
        """
        Time interval (in seconds) for testing speed: the speed is calculated according to the difference in
        (x,y) coordinates over a time interval at least this long.
        """
        return self._calc_speed_interval

    @calc_speed_interval.setter
    def calc_speed_interval(self, value):
        if value is None:
            value = 0

        if not isinstance(value, numbers.Number):
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_numeric.format(type(self), "calc_speed_interval", value))
        if value < 0:
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_negative.format(type(self), "calc_speed_interval", value))

        self._calc_speed_interval = value
