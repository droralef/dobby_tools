"""

Local speed validator: Validate minimal/maximal instantaneous speed

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import numpy as np
import numbers
from enum import Enum

import dobbyt


# noinspection PyAttributeOutsideInit
class InstantaneousSpeedValidator(dobbyt._Dobby_Object):
    """
    Validator for momentary (instantanesous) speed: make sure that at each given moment, the
    movement speed is within the valid boundaries

    The min/max speed are configured as mm/sec, but the movement progress is provided in arbitrary units
    (e.g., pixels). You'll therefore need to define the units-per-mm ratio.
    """

    Axis = Enum('Axis', 'x y xy')

    ErrType = Enum('ErrType', 'OK TooSlow TooFast')

    #-----------------------------------------------------------------------------------
    def __init__(self, units_per_mm, axis=Axis.y, enabled=False, min_speed=None, max_speed=None,
                 grace_period=0, calc_speed_interval=0):
        """
        Constructor
        :param units_per_mm: The ratio of units (provided in the call to :func:`~dobbyt.movement.InstantaneousSpeedValidator.mouse_at`) per mm
        :param axis: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.axis`
        :param enabled: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.enabled`
        :param min_speed: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.min_speed`
        :param max_speed: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.max_speed`
        :param grace_period: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.grace_period`
        :param calc_speed_interval: See :func:`~dobbyt.movement.InstantaneousSpeedValidator.calc_speed_interval`
        """

        super(InstantaneousSpeedValidator, self).__init__()

        if not isinstance(units_per_mm, numbers.Number):
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_numeric.format("units_per_mm", units_per_mm))

        self._units_per_mm = units_per_mm

        self.enabled = enabled
        self.axis = axis
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.grace_period = grace_period
        self.calc_speed_interval = calc_speed_interval

        self.reset()


    #========================================================================
    #      API
    #========================================================================

    _errmsg_mouse_at_non_numeric = "dobbyt error: InstantaneousSpeedValidator.mouse_at was called with a non-numeric {0} ({1})"

    #-----------------------------------------------------------------------------------
    def reset(self):
        """
        Called when a trial starts - reset any previous movement
        """
        self._prev_locations = []

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
            return InstantaneousSpeedValidator.ErrType.OK

        #-- Validate types
        if not isinstance(x_coord, numbers.Number):
            raise AttributeError(InstantaneousSpeedValidator._errmsg_mouse_at_non_numeric.format("x_coord", x_coord))
        if not isinstance(y_coord, numbers.Number):
            raise AttributeError(InstantaneousSpeedValidator._errmsg_mouse_at_non_numeric.format("y_coord", y_coord))
        if not isinstance(time, numbers.Number):
            raise AttributeError(InstantaneousSpeedValidator._errmsg_mouse_at_non_numeric.format("time", time))

        #-- Validate that times are provided in increasing order
        if len(self._prev_locations) > 0 and self._prev_locations[-1][2] > time:
            raise dobbyt.InvalidStateError("InstantaneousSpeedValidator.mouse_at was called with time={0} after it was previously called with time={1}".format(time, self._prev_locations[-1][2]))

        curr_xyt = (x_coord / self._units_per_mm, y_coord / self._units_per_mm, time)

        latest_prev_time = time - self._calc_speed_interval
        self._leave_just_one_prev_loc_older_than(latest_prev_time)
        print 'left %d entries' % len(self._prev_locations)

        #-- Remember current coords & time
        self._prev_locations.append(curr_xyt)

        #-- Calculate speed, if possible
        if len(self._prev_locations) > 1 \
                and self._prev_locations[0][2] <= latest_prev_time \
                and (self._grace_period is None or time > self._grace_period):

            speed = self._calc_speed_func(self._prev_locations[0], curr_xyt)
            print 'speed=%f' % speed

            if self._min_speed is not None and speed < self._min_speed:
                return InstantaneousSpeedValidator.ErrType.TooSlow

            if self._max_speed is not None and speed > self._max_speed:
                return InstantaneousSpeedValidator.ErrType.TooFast

        return InstantaneousSpeedValidator.ErrType.OK

    #----------------
    def _leave_just_one_prev_loc_older_than(self, max_time):
        older_than_threshold = np.where([p[2] <= max_time for p in self._prev_locations])
        older_than_threshold = older_than_threshold[0]
        if len(older_than_threshold) > 1:
            self._prev_locations = self._prev_locations[older_than_threshold[-1]:]

    #----------------
    @staticmethod
    def _calc_speed_x(xyt1, xyt2):
        dx = xyt2[0] - xyt1[0]
        dt = xyt2[2] - xyt1[2]
        return dx / dt

    @staticmethod
    def _calc_speed_y(xyt1, xyt2):
        dy = xyt2[1] - xyt1[1]
        dt = xyt2[2] - xyt1[2]
        print 'dy=%.2f  dt=%.2f' % (dy, dt)
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
        """
        The axis on which speed is validated (type = InstantaneousSpeedValidator.Axis)
        Axis.x or Axis.y: limit the speed in the relevant axis.
        Axis.xy: limit the diagonal speed
        """
        return self._axis

    @axis.setter
    def axis(self, value):

        if value == InstantaneousSpeedValidator.Axis.x:
            self._calc_speed_func = InstantaneousSpeedValidator._calc_speed_x
        elif value == InstantaneousSpeedValidator.Axis.y:
            self._calc_speed_func = InstantaneousSpeedValidator._calc_speed_y
        elif value == InstantaneousSpeedValidator.Axis.xy:
            self._calc_speed_func = InstantaneousSpeedValidator._calc_speed_xy
        else:
            raise AttributeError("dobbyt error: invalid value ({0}) for InstantaneousSpeedValidator.axis - expecting a value of type InstantaneousSpeedValidator.Axis".format(value))

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
                raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_numeric.format("min_speed", value))
            if value <= 0:
                raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_positive.format("min_speed", value))

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
                raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_numeric.format("max_speed", value))
            if value <= 0:
                raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_positive.format("max_speed", value))

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
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_numeric.format("grace_period", value))
        if value < 0:
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_negative.format("grace_period", value))

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
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_non_numeric.format("calc_speed_interval", value))
        if value < 0:
            raise AttributeError(InstantaneousSpeedValidator._errmsg_set_to_negative.format("calc_speed_interval", value))

        self._calc_speed_interval = value
