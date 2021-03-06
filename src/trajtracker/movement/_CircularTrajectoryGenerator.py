"""

Trajectory generators (to be used by StimulusAnimator)

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division
import numbers
import numpy as np

import trajtracker
import trajtracker._utils as _u


class CircularTrajectoryGenerator(trajtracker._TTrkObject):
    """
    Generate a circular movement trajectory for a stimulus.

    Use this class in conjunction with :class:`~trajtracker.movement.StimulusAnimator`
    """

    def __init__(self, center=None, radius=None, degrees_per_sec=None, degrees_at_t0=None):
        """
        Constructor

        :param center: See :attr:`~trajtracker.movement.CircularTrajectoryGenerator.center`
        :param radius: See :attr:`~trajtracker.movement.CircularTrajectoryGenerator.radius`
        :param degrees_per_sec: See :attr:`~trajtracker.movement.CircularTrajectoryGenerator.degrees_per_sec`
        :param degrees_at_t0: See :attr:`~trajtracker.movement.CircularTrajectoryGenerator.degrees_at_t0`
        """
        super(CircularTrajectoryGenerator, self).__init__()

        if center is not None:
            self.center = center

        if radius is not None:
            self.radius = radius

        if degrees_per_sec is not None:
            self.degrees_per_sec = degrees_per_sec

        self.degrees_at_t0 = degrees_at_t0


    #============================================================================
    #     Generate trajectory
    #============================================================================

    def get_traj_point(self, time):
        """
        Return the trajectory info at a certain time

        :param time: in seconds
        :returns: a dict with the coordinates ('x' and 'y' entries).
        """

        _u.validate_func_arg_type(self, "get_xy", "time", time, numbers.Number)
        if not hasattr(self, "_center"):
            raise trajtracker.InvalidStateError("trajtracker error: {:}.get_xy() was called without setting center".format(type(self).__name__))
        if not hasattr(self, "_degrees_per_sec"):
            raise trajtracker.InvalidStateError("trajtracker error: {:}.get_xy() was called without setting degrees_per_sec".format(type(self).__name__))
        if not hasattr(self, "_radius"):
            raise trajtracker.InvalidStateError("trajtracker error: {:}.get_xy() was called without setting radius".format(type(self).__name__))

        curr_degrees = (self._degrees_at_t0 + self._degrees_per_sec * time) % 360

        curr_degrees_rad = curr_degrees / 360 * np.pi * 2

        x = int(np.abs(np.round(self._radius * np.sin(curr_degrees_rad))))
        y = int(np.abs(np.round(self._radius * np.cos(curr_degrees_rad))))

        if curr_degrees > 180:
            x = -x
        if 90 < curr_degrees < 270:
            y = -y

        return {'x': x + self._center[0], 'y': y + self._center[1]}


    #============================================================================
    #     Configure
    #============================================================================

    #------------------------------------------------------------
    @property
    def center(self):
        """
        The center of the circle (x,y coordinates)
        """
        return self._center

    @center.setter
    def center(self, value):
        value = _u.validate_attr_is_coord(self, "center", value)
        self._center = value


    #------------------------------------------------------------
    @property
    def radius(self):
        """
        The radius of the circle
        """
        return self._radius

    @radius.setter
    def radius(self, value):
        _u.validate_attr_type(self, "radius", value, numbers.Number)
        _u.validate_attr_positive(self, "radius", value)
        self._radius = value

    #------------------------------------------------------------
    @property
    def degrees_per_sec(self):
        """
        The radial speed of movement (you can also specify the speed as
        :attr:`~trajtracker.movement.CircularTrajectoryGenerator.full_rotation_duration`)
        """
        return self._degrees_per_sec

    @degrees_per_sec.setter
    def degrees_per_sec(self, value):
        _u.validate_attr_type(self, "degrees_per_sec", value, numbers.Number)
        _u.validate_attr_positive(self, "degrees_per_sec", value)
        self._degrees_per_sec = value % 360

    #------------------------------------------------------------
    @property
    def full_rotation_duration(self):
        """
        The radial speed of movement, in seconds (you can also specify the speed as
        :attr:`~trajtracker.movement.CircularTrajectoryGenerator.degrees_per_sec`)
        """
        return 360 / self._degrees_per_sec

    @full_rotation_duration.setter
    def full_rotation_duration(self, value):
        _u.validate_attr_type(self, "degrees_per_sec", value, numbers.Number)
        _u.validate_attr_positive(self, "degrees_per_sec", value)
        self._degrees_per_sec = (360 / value) % 360

    #------------------------------------------------------------
    @property
    def degrees_at_t0(self):
        """
        Position (specified as degrees) where the stimulus should be at time=0
        """
        return self._degrees_at_t0

    @degrees_at_t0.setter
    def degrees_at_t0(self, value):
        value = _u.validate_attr_numeric(self, "degrees_at_t0", value, none_value=_u.NoneValues.ChangeTo0)
        self._degrees_at_t0 = value % 360

