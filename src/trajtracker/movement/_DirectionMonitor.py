"""

Movement monitor: continuously track the movement direction

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import numbers

import numpy as np
from enum import Enum

import trajtracker
import trajtracker._utils as _u
import trajtracker.utils as u


class DirectionMonitor(trajtracker._TTrkObject):
    """
    Monitor the mouse/finger direction.

    This class also maintains some information about curves in the trajectory.
    """


    Units = Enum("Units", "Degrees Radians")


    #-------------------------------------------------------------------------
    def __init__(self, units_per_mm, min_distance=0, angle_units=Units.Degrees, zero_angle=0, min_angle_change_per_curve=0):
        """
        Constructor

        :param units_per_mm: See :attr:`~trajtracker.movement.DirectionMonitor.units_per_mm`
        :param min_distance: See :attr:`~trajtracker.movement.DirectionMonitor.min_distance`
        :param angle_units: See :attr:`~trajtracker.movement.DirectionMonitor.angle_units`
        :param min_angle_change_per_curve: See :attr:`~trajtracker.movement.DirectionMonitor.min_angle_change_per_curve`
        """
        super(DirectionMonitor, self).__init__()

        _u.validate_func_arg_type(self, "__init__", "units_per_mm", units_per_mm, numbers.Number)
        _u.validate_func_arg_positive(self, "__init__", "units_per_mm", units_per_mm)
        self._units_per_mm = units_per_mm

        self.min_distance = min_distance
        self.angle_units = angle_units
        self.zero_angle = zero_angle
        self.min_angle_change_per_curve = min_angle_change_per_curve

        self.reset()



    #====================================================================================
    #   Runtime API - update movement
    #====================================================================================


    #-------------------------------------------------------------------------
    def reset(self):
        """
        Called when a trial starts - reset any previous movement
        """
        self._recent_near_coords = []
        self._pre_recent_coord = None

        self._curr_angle = None

        #-- "current curve" is a curve that is validated
        self._curr_curve_direction = None
        self._curr_curve_start_angle = None
        self._curr_curve_start_index = None

        #-- "new curve" is when we observe a very small change in angle, but we're not yet sure
        #-- it should count as a curve.
        self._possible_curve_direction = None
        self._possible_curve_start_angle = None
        self._possible_curve_start_index = None

        self._n_curves = 0


    #-------------------------------------------------------------------------
    # noinspection PyIncorrectDocstring
    def update_xyt(self, x_coord, y_coord, time):
        """
        Call this method whenever the finger/mouse moves
        """

        _u.validate_func_arg_type(self, "update_xyt", "x_coord", x_coord, numbers.Number)
        _u.validate_func_arg_type(self, "update_xyt", "y_coord", y_coord, numbers.Number)
        _u.validate_func_arg_type(self, "update_xyt", "time", time, numbers.Number)
        _u.validate_func_arg_not_negative(self, "update_xyt", "time", time)

        self._remove_far_enough_recent_coords(x_coord, y_coord)

        # remember coordinates
        self._recent_near_coords.append((x_coord, y_coord, time))

        last_angle = self._curr_angle
        self._calc_curr_angle()
        self._check_if_new_curve(last_angle)


    #-------------------------------------
    # Calculate the recent movement direction
    #
    def _calc_curr_angle(self):

        if self._pre_recent_coord is None:
            self._curr_angle = None
            return

        angle = u.get_angle(self._pre_recent_coord, self._recent_near_coords[-1])

        if self._angle_units == self.Units.Degrees:
            angle = angle / (np.pi * 2) * 360

        if self._zero_angle != 0:
            angle -= self._zero_angle

        max_angle = self._max_angle()
        angle = angle % max_angle
        if angle > max_angle / 2:
            angle -= max_angle

        self._curr_angle = angle


    #-------------------------------------
    def _max_angle(self):
        return 360 if self._angle_units == self.Units.Degrees else np.pi * 2


    #-------------------------------------
    def _check_if_new_curve(self, prev_angle):

        if self._curr_angle is None or prev_angle is None:
            return

        max_angle = self._max_angle()
        change_in_angle = (self._curr_angle - prev_angle) % max_angle
        if change_in_angle == 0:
            return

        curr_curve_direction = 1 if change_in_angle <= max_angle / 2 else -1

        #-- Compare the angular acceleration's direction between existing curve and new data
        if curr_curve_direction == self._curr_curve_direction:

            #-- Angular acceleration remained in the same direction: we're still in the same curve
            self._clear_possible_curve()

        else:
            #-- Angular acceleration changed its direction: this may be a new curve

            if self._possible_curve_direction is None:
                #-- Mark the beginning of a possible curve
                self._possible_curve_direction = curr_curve_direction
                self._possible_curve_start_angle = self._curr_angle
                self._possible_curve_start_index = len(self._recent_near_coords) - 1
                self._last_pre_curve_angle = prev_angle

            #-- Check if the finger/mouse changed its direction enough
            change_in_angle_along_curve = (self._curr_angle - self._last_pre_curve_angle) % max_angle
            change_in_angle_along_curve = min(change_in_angle_along_curve, max_angle-change_in_angle_along_curve)

            if change_in_angle_along_curve >= self._min_angle_change_per_curve:
                #-- The change in angle is large enough: this counts as a new curve

                self._n_curves += 1

                self._curr_curve_direction = curr_curve_direction
                self._curr_curve_start_angle = self._curr_angle
                self._curr_curve_start_index = len(self._recent_near_coords) - 1

                self._clear_possible_curve()



    #-------------------------------------------------
    def _clear_possible_curve(self):
        self._possible_curve_direction = None
        self._possible_curve_start_angle = None
        self._possible_curve_start_index = None
        self._last_pre_curve_angle = None

    #-------------------------------------
    # Remove the first entries in self._prev_locations, as long as the first entry remains far enough
    # for angle computation (i.e., farther than self._calc_angle_interval)
    #
    # Returns True if, after this function call, self._prev_locations[0] is far enough for angle computation
    #
    def _remove_far_enough_recent_coords(self, x_coord, y_coord):

        if len(self._recent_near_coords) == 0:
            return

        sq_min_distance = (self._min_distance * self._units_per_mm) ** 2

        self._pre_recent_coord = None

        #-- Find the latest coordinate that is far enough
        for i in range(len(self._recent_near_coords)-1, -1, -1):
            x, y, t = self._recent_near_coords[i]
            if (x - x_coord) ** 2 + (y - y_coord) ** 2 >= sq_min_distance:
                #-- This coordinate is far enough
                self._pre_recent_coord = (x, y)
                break


    #====================================================================================
    #   Runtime API - get info
    #====================================================================================

    #-------------------------------------
    @property
    def curr_angle(self):
        """ The angle where the finger/mouse is now going at """
        return self._curr_angle

    #-------------------------------------
    @property
    def curr_curve_direction(self):
        """
        The direction of the current curve (i.e., to which direction the mouse/finger currently turns)
        1 = clockwise, -1 = counter clockwise
        """
        return self._curr_curve_direction

    # -------------------------------------
    @property
    def curr_curve_start_angle(self):
        """
        The finger/mouse angle at the beginning of the current curve
        """
        return self._curr_curve_start_angle

    # -------------------------------------
    @property
    def curr_curve_start_xyt(self):
        """
        The coordinates and time at the beginning of the current curve
        """
        if self._curr_curve_start_index is None:
            return None
        else:
            return self._recent_near_coords[self._curr_curve_start_index]

    #-------------------------------------
    @property
    def n_curves(self):
        """
        The number of curves since the last call to reset()
        """
        return self._n_curves


    #====================================================================================
    #   Configure
    #====================================================================================

    #-------------------------------------
    @property
    def units_per_mm(self):
        """
        The ratio of units (provided in the call to :func:`~trajtracker.movement.DirectionMonitor.update_xyt`) per mm.
        This is relevant only for :attr:`~trajtracker.movement.DirectionMonitor.min_distance`
        """
        return self._units_per_mm


    #-------------------------------------
    @property
    def min_distance(self):
        """ The minimal distance (in mm) between points required for calculating direction """
        return self._min_distance

    @min_distance.setter
    def min_distance(self, value):
        _u.validate_attr_numeric(self, "min_distance", value)
        _u.validate_attr_not_negative(self, "min_distance", value)
        self._min_distance = value
        self._log_setter("min_distance")


    #-------------------------------------
    @property
    def angle_units(self):
        """
        Units for specifying angles (Units.Degrees or Units.Radians)
        """
        return self._angle_units

    @angle_units.setter
    def angle_units(self, value):
        _u.validate_attr_type(self, "angle_units", value, self.Units)
        self._angle_units = value
        self._log_setter("angle_units")

    #-------------------------------------
    @property
    def zero_angle(self):
        """
        The angle that counts as zero (0=up).
        This means that:
        - the value returned from :attr:`~trajtracker.movement.DirectionMonitor.curr_angle` will be rotated by this value
        - The counting of left/right curves will be relatively to this zero angle
        """
        return self._zero_angle

    @zero_angle.setter
    def zero_angle(self, value):
        _u.validate_attr_numeric(self, "zero_angle", value)
        self._zero_angle = value
        self._log_setter("zero_angle")


    #-------------------------------------
    @property
    def min_angle_change_per_curve(self):
        """
        A curve must change the finger/mouse direction by at least this amount.
        Smaller changes do not count as curves.
        """
        return self._min_angle_change_per_curve

    @min_angle_change_per_curve.setter
    def min_angle_change_per_curve(self, value):
        _u.validate_attr_numeric(self, "min_angle_change_per_curve", value)
        _u.validate_attr_not_negative(self, "min_angle_change_per_curve", value)
        self._min_angle_change_per_curve = value
        self._log_setter("min_angle_change_per_curve")
