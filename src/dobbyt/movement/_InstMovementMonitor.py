"""

Movement monitor: continuously track speed, direction, etc.

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division
import numbers
import numpy as np

import dobbyt
from dobbyt.misc._utils import ErrMsg, BaseValidator


class InstMovementMonitor(dobbyt._Dobby_Object):
    """
    This object monitors the mouse/finger movement and can get info about the instantaneous movement
    direction and speed.
    """


    #-------------------------------------------------------------------------
    def __init__(self, units_per_mm, calculation_interval):
        """
        Constructor
        :param units_per_mm: See :func:`~dobbyt.movement.InstMovementMonitor.units_per_mm`
        :param calculation_interval: See :func:`~dobbyt.movement.InstMovementMonitor.calculation_interval`
        """
        super(InstMovementMonitor, self).__init__()

        self.units_per_mm = units_per_mm
        self.calculation_interval = calculation_interval

        self.reset()



    #====================================================================================
    #   Runtime API - update movement
    #====================================================================================


    #-------------------------------------------------------------------------
    def reset(self, time=None):
        """
        Called when a trial starts - reset any previous movement
        :param time: The time when the trial starts.
        """
        if time is not None and not isinstance(time, (int, float)):
            raise ValueError(ErrMsg.invalid_method_arg_type(self.__class__, "reset", "numeric", "time", time))

        self._recent_points = []
        self._pre_recent_point = None
        self._time0 = time


    #-------------------------------------------------------------------------
    def mouse_at(self, x_coord, y_coord, time):
        """
        Call this method whenever the finger/mouse moves
        :param time: use the same time scale provided to reset()
        """

        # noinspection PyProtectedMember
        BaseValidator._mouse_at_validate_xyt(self, x_coord, y_coord, time)
        self._mouse_at_validate_time(time)

        if self._time0 is None:
            self._time0 = time

        #-- Set coordinate space
        x_coord /= self._units_per_mm
        y_coord /= self._units_per_mm

        #-- Find distance to recent coordinate
        if len(self._recent_points) > 0:
            last_loc = self._recent_points[-1]
            distance = np.sqrt((x_coord-last_loc[0]) ** 2 + (y_coord-last_loc[1]) ** 2)
        else:
            distance = 0

        self._remove_recent_points_older_than(time - self._calculation_interval)

        #-- Remember current coords & time
        self._recent_points.append((x_coord, y_coord, time, distance))


    #--------------------------------------
    def _mouse_at_validate_time(self, time):

        #-- Validate that times are provided in increasing order
        prev_time = self._recent_points[-1][2] if len(self._recent_points) > 0 else self._time0
        if prev_time is not None and prev_time > time:
            raise dobbyt.InvalidStateError("{0}.mouse_at() was called with time={1} after it was previously called with time={2}".format(self.__class__, time, prev_time))


    #--------------------------------------
    # Remove all _recent_points that are older than the given threshold.
    # Remember the newest removed point.
    #
    def _remove_recent_points_older_than(self, latest_good_time):

        older_than_threshold = np.where([p[2] <= latest_good_time for p in self._recent_points])
        older_than_threshold = older_than_threshold[0]
        if len(older_than_threshold) >= 1:
            self._pre_recent_point = self._recent_points[older_than_threshold[-1]]
            self._recent_points = self._recent_points[older_than_threshold[-1]+1:]


    #====================================================================================
    #   Runtime API - get info about movement
    #====================================================================================

    #-------------------------------------------------------------------------
    @property
    def time_in_trial(self):
        """ Time elapsed since trial started (sec) """

        if self._time0 is None or len(self._recent_points) == 0:
            return None

        return self._recent_points[-1][2] - self._time0


    #-------------------------------------------------------------------------
    @property
    def xspeed(self):
        """ The instantaneous speed (mm/sec) """

        if self._pre_recent_point is None:
            return None

        y1 = self._pre_recent_point[0]
        y2 = self._recent_points[-1][0]
        return (y2-y1) / self.last_calculation_interval


    #-------------------------------------------------------------------------
    @property
    def yspeed(self):
        """ The instantaneous speed (mm/sec) """

        if self._pre_recent_point is None:
            return None

        y1 = self._pre_recent_point[1]
        y2 = self._recent_points[-1][1]
        return (y2-y1) / self.last_calculation_interval


    #-------------------------------------------------------------------------
    @property
    def xyspeed(self):
        """ The instantaneous speed (mm/sec) """

        if self._pre_recent_point is None:
            return None

        distance = sum([loc[3] for loc in self._recent_points])
        return distance / self.last_calculation_interval


    #-------------------------------------------------------------------------
    @property
    def angle(self):
        """ The instantaneous movement angle (mm/sec) """

        if self._pre_recent_point is None:
            return None

        xy1 = self._pre_recent_point[0:1]
        xy2 = self._recent_points[-1][0:1]

        #todo fix # Based on comparing two locations
        pass


    #-------------------------------------------------------------------------
    @property
    def last_calculation_interval(self):
        """ The time interval (sec) used for the last calculation of speed & direction """

        if self._pre_recent_point is None:
            return None
        else:
            return self._recent_points[-1][2] - self._pre_recent_point[2]


    #====================================================================================
    #   Properties
    #====================================================================================

    #-------------------------------------------------------------------------
    @property
    def units_per_mm(self):
        """
        The ratio of units (provided in the call to :func:`~dobbyt.movement.MovementMonitor.mouse_at`) per mm
        """
        return self._units_per_mm


    @units_per_mm.setter
    def units_per_mm(self, value):
        if not isinstance(value, numbers.Number):
            raise ValueError(ErrMsg.attr_invalid_type(self.__class__, "units_per_mm", "numeric", value))
        if value <= 0:
            raise ValueError(ErrMsg.attr_non_positive(self.__class__, "units_per_mm", value))

        self._units_per_mm = value


    #-------------------------------------------------------------------------
    @property
    def calculation_interval(self):
        """
        The time interval (in seconds) over which calculations are performed.
        Use shorter time period if available
        """
        return self._calculation_interval


    @calculation_interval.setter
    def calculation_interval(self, value):
        if not isinstance(value, numbers.Number):
            raise ValueError(ErrMsg.attr_invalid_type(self.__class__, "calculation_interval", "numeric", value))
        if value <= 0:
            raise ValueError(ErrMsg.attr_non_positive(self.__class__, "calculation_interval", value))

        self._calculation_interval = value


