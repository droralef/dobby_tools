"""

 Validate the finger direction

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division
import numbers
import numpy as np

import dobbyt


class DirectionValidator(dobbyt._Dobby_Object):

    def __init__(self, units_per_mm, min_angle=None, max_angle=None, calc_angle_interval=None, enabled=False):
        """
        Constructor
        :param units_per_mm: The ratio of units (provided in the call to :func:`~dobbyt.movement.InstantaneousSpeedValidator.mouse_at`) per mm
        :param min_angle: See :func:`~dobbyt.movement.DirectionValidator.min_angle`
        :param max_angle: See :func:`~dobbyt.movement.DirectionValidator.max_angle`
        :param calc_angle_interval: See :func:`~dobbyt.movement.DirectionValidator.calc_angle_interval`
        :param enabled: See :func:`~dobbyt.movement.DirectionValidator.enabloed`
        """
        super(DirectionValidator, self).__init__()

        if not isinstance(units_per_mm, numbers.Number) or units_per_mm <= 0:
            raise ValueError("dobbyt error: invalid units_per_mm argument ({0}) to constructor of {1}".format(units_per_mm, type(self)))

        self._units_per_mm = units_per_mm

        self.enabled = enabled
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.calc_angle_interval = calc_angle_interval


    #========================================================================
    #      Validation API
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
            return DirectionValidator.ErrType.OK

        self._validate_xyt(x_coord, y_coord, time)

        curr_xyt = (x_coord / self._units_per_mm, y_coord / self._units_per_mm, time)

        latest_prev_time = time - self._calc_angle_interval
        can_compute_angle = self._remove_far_enough_prev_locations(x_coord, y_coord)

        #-- Remember current coords & time
        self._prev_locations.append(curr_xyt)

        x0, y0, t0 = self._prev_locations[0]

        #-- Calculate speed, if possible
        if can_compute_angle and (x0, y0) != (x_coord, y_coord):
            angle = self._calc_angle((x0, y0), (x_coord, y_coord))

            return self._test_angle(angle)

        return DirectionValidator.ErrType.OK

    #----------------
    def _validate_xyt(self, x_coord, y_coord, time):
        #-- Validate types
        if not isinstance(x_coord, numbers.Number):
            raise AttributeError(self._errmsg_mouse_at_non_numeric.format("x_coord", x_coord))
        if not isinstance(y_coord, numbers.Number):
            raise AttributeError(self._errmsg_mouse_at_non_numeric.format("y_coord", y_coord))
        if not isinstance(time, numbers.Number):
            raise AttributeError(self._errmsg_mouse_at_non_numeric.format("time", time))

        if len(self._prev_locations) > 0 and self._prev_locations[-1][2] > time:
            raise dobbyt.InvalidStateError("{0}.mouse_at() was called with time={1} after it was previously called with time={2}".format(type(self), time, self._prev_locations[-1][2]))


    #-------------------------------------
    # Remove the first entries in self._prev_locations, as long as the first entry remains far enough
    # for angle computation (i.e., farther than self._calc_angle_interval)
    #
    # Returns True if, after this function call, self._prev_locations[0] is far enough for angle computation
    #
    def _remove_far_enough_prev_locations(self, x_coord, y_coord):

        distance2 = self._calc_angle_interval ** 2
        use_ind = None
        for i in range(len(self._prev_locations)):
            x, y, t = self._prev_locations[i]
            if (x-x_coord)**2 + (y-y_coord)**2 < distance2:
                use_ind = i-1
                break

        if use_ind is not None and use_ind>0:
            self._prev_locations = self._prev_locations[use_ind:]

        return len(self._prev_locations) > 0 and use_ind > 0

    #-------------------------------------
    @staticmethod
    def _calc_angle(point1, point2):

        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]

        if dx==0:
            return np.sign(dy) * np.pi
        else:
            return np.arctan(dy/dx)

    #-------------------------------------
    def _test_angle(self, angle):
        pass

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
            raise AttributeError(DirectionValidator._errmsg_set_to_non_boolean.format("enabled", value))

        self._enabled = value

    #-----------------------------------------------------------------------------------
    @property
    def min_angle(self):
        """
        The minimal valid angle (in degrees)
        This value can be either smaller or larger than :func:`~dobbyt.movement.DirectionValidator.max_angle`
        """
        return self._min_angle

    @min_angle.setter
    def min_angle(self, value):
        if value is not None and not isinstance(value, (int, float)):
            raise AttributeError(DirectionValidator._errmsg_set_to_non_numeric.format("min_angle", value))
        self._min_angle = value % 360

    #-----------------------------------------------------------------------------------
    @property
    def max_angle(self):
        """
        The maximal valid angle (in degrees)
        This value can be either smaller or larger than :func:`~dobbyt.movement.DirectionValidator.min_angle`
        """
        return self._max_angle

    @max_angle.setter
    def max_angle(self, value):
        if value is not None and not isinstance(value, (int, float)):
            raise AttributeError(DirectionValidator._errmsg_set_to_non_numeric.format("max_angle", value))
        self._max_angle = value % 360

    #-----------------------------------------------------------------------------------
    @property
    def calc_angle_interval(self):
        """
        Time minimal distance (in mm) over which a direction vector can be calculated
        """
        return self._calc_angle_interval

    @calc_angle_interval.setter
    def calc_angle_interval(self, value):
        if value is None:
            value = 0

        if not isinstance(value, numbers.Number):
            raise AttributeError(DirectionValidator._errmsg_set_to_non_numeric.format("calc_angle_interval", value))
        if value < 0:
            raise AttributeError(DirectionValidator._errmsg_set_to_negative.format("calc_angle_interval", value))

        self._calc_angle_interval = value
