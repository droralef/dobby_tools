"""

Validator for minimal/maximal global speed

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import numbers

import numpy as np

import dobbyt
from dobbyt.misc._utils import BaseValidator, ErrMsg
from dobbyt.validators import ValidationAxis, ValidationFailed


# noinspection PyAttributeOutsideInit
class GlobalSpeedValidator(BaseValidator):
    """
    Validate minimal movement speed.
    The validation is of the *average* speed per trial. The validator can also interpolate the speed limit,
    i.e., impose the limit on the average speed from time=0 until any time point during the trial.
    """

    err_too_slow = "too_slow"


    class Section(object):
        def __init__(self, time_percentage, distance_percentage):
            self.time_percentage = time_percentage
            self.distance_percentage = distance_percentage
            self.duration = None
            self.length = None


    #-----------------------------------------------------------------------------------
    def __init__(self, enabled=False, origin_coord=None, end_coord=None, axis=ValidationAxis.y,
                 grace_period=None, sections=None):

        super(GlobalSpeedValidator, self).__init__()

        self.enabled = enabled
        self.axis = axis
        self.grace_period = grace_period
        self.sections = sections

        self._origin_coord = None
        if origin_coord is not None:
            self.origin_coord = origin_coord
        self._end_coord = None
        if end_coord is not None:
            self.end_coord = end_coord


    #========================================================================
    #      Validation API
    #========================================================================

    #----------------------------------------------------------------------------------
    def reset(self, time=0):

        if time is not None and not isinstance(time, (int, float)):
            raise ValueError(ErrMsg.invalid_method_arg_type(self.__class__, "reset", "numeric", "time", time))

        self._time0 = time
        self._prepare_expected_coords()


    #----------------------------------------------------------------------------------
    def _prepare_expected_coords(self):
        #TODO: when is it really the best to call this function? On start-of-trial? On any change?

        total_distance = self._end_coord - self._origin_coord

        for section in self._sections:
            section.duration = self.max_trial_duration * section.time_percentage
            section.length = total_distance * section.distance_percentage
            section.expected_velocity = section.length / section.duration


    #----------------------------------------------------------------------------------
    def mouse_at(self, x_coord, y_coord, time):
        """
        Validate movement. Thro
        :param x_coord: Current x coordinates
        :param y_coord: Current x coordinates
        :param time: Time from start of trial
        :raises dobbyt.ValidationFailed:
        """
        self.mouse_at_validate_xyt(x_coord, y_coord, time)

        #-- If this is the first call in a trial: do nothing
        if self._time0 is None:
            self.reset(time)
            return False

        if time < self._time0:
            raise dobbyt.InvalidStateError("{0}.mouse_at() was called with time={1}, but the trial started at time={2}".format(self.__class__, time, self._time0))

        time -= self._time0

        #-- No validation during grace period
        if time <= self._grace_period:
            return False

        #-- Get the expected and actual coordinates
        coord = x_coord if self._axis == ValidationAxis.x else y_coord
        expected_coord = self.get_expected_coord_at_time(time)
        d_coord = coord - expected_coord

        #-- Actual coordinate must be ahead of the expected minimum
        if np.sign(d_coord) != np.sign(self._end_coord - self._origin_coord):
            raise ValidationFailed(self.err_too_slow, "You moved too slowly", self)

    #----------------------------------------------------------------------------------
    # Get the coordinate expected
    #
    #
    def get_expected_coord_at_time(self, time):

        remaining_time = time
        result = 0
        for section in self._sections:
            if remaining_time > section.duration:
                remaining_time -= section.duration
                result += section.length
            else:
                result += section.length * (remaining_time / section.duration)
                break

        return result

    #========================================================================
    #      Config
    #========================================================================

    #-----------------------------------------------------------------------------------
    @property
    def enabled(self):
        """Whether the validator is currently enabled (boolean)"""
        return self._enabled

    @enabled.setter
    def enabled(self, value):

        if not isinstance(value, bool):
            raise AttributeError(ErrMsg.attr_invalid_type(self.__class__, "enabled", bool, value))

        self._enabled = value

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
        if value == ValidationAxis.xy:
            raise AttributeError(ErrMsg.attr_invalid_value(self.__class__, "axis", value))

        self._axis = value

    #-----------------------------------------------------------------------------------
    @property
    def origin_coord(self):
        """
        The coordinate (x or y) in which the speed validation starts
        The value of this attribute is a single number
        """
        return self._origin_coord

    @origin_coord.setter
    def origin_coord(self, value):
        self.validate_numeric("origin_coord", value, BaseValidator.NoneValues.Invalid)
        self._origin_coord = value

    #-----------------------------------------------------------------------------------
    @property
    def end_coord(self):
        """
        The coordinate (x or y) in which the speed validation end (i.e., end-of-trial coordinate)
        The value of this attribute is a single number
        """
        return self._end_coord

    @end_coord.setter
    def end_coord(self, value):
        self.validate_numeric("end_coord", value, BaseValidator.NoneValues.Invalid)
        self._end_coord = value


    #-----------------------------------------------------------------------------------
    @property
    def grace_period(self):
        """The grace period in the beginning of each trial, during which speed is not validated (in seconds)."""
        return self._grace_period

    @grace_period.setter
    def grace_period(self, value):
        value = self.validate_numeric("grace_period", value, BaseValidator.NoneValues.ChangeTo0)
        self.validate_not_negative("grace_period", value)
        self._grace_period = value

    #-----------------------------------------------------------------------------------
    @property
    def max_trial_duration(self):
        """The maximal duration of a trial (in seconds)."""
        return self._max_trial_duration

    @max_trial_duration.setter
    def max_trial_duration(self, value):
        value = self.validate_numeric("max_trial_duration", value, BaseValidator.NoneValues.ChangeTo0)
        self.validate_not_negative("max_trial_duration", value)
        self._max_trial_duration = value

    #-----------------------------------------------------------------------------------

    _errmsg_sections_not_percentage = "dobbyt error: invalid {0} for {1}.sections[{2}]: expecting a number between 0 and 1"

    @property
    def sections(self):
        #TODO: add comment
        return self._sections #TODO: clone limits

    @sections.setter
    def sections(self, value):
        if value is None:
            value = []

        if not isinstance(value, (tuple, list)):
            raise AttributeError("dobbyt error: invalid value for {0}.sections ({1}) - expecting a list of 'TimeLimit' objects".format(self.__class__, value))

        sections = []
        for i in range(len(value)):
            lim = value[i]
            if not isinstance(lim, GlobalSpeedValidator.Section):
                raise AttributeError("dobbyt error: invalid value for {0}.sections - expecting a list of 'Section' objects".format(self.__class__))

            if not isinstance(lim.distance_percentage, numbers.Number):
                raise AttributeError(GlobalSpeedValidator._errmsg_sections_not_percentage.format("distance_percentage", self.__class__, i))
            if not (0 < lim.distance_percentage < 1):
                raise AttributeError(GlobalSpeedValidator._errmsg_sections_not_percentage.format("distance_percentage", self.__class__, i))

            if not isinstance(lim.time_percentage, numbers.Number):
                raise AttributeError(GlobalSpeedValidator._errmsg_sections_not_percentage.format("time_percentage", self.__class__, i))
            if not (0 < lim.time_percentage < 1):
                raise AttributeError(GlobalSpeedValidator._errmsg_sections_not_percentage.format("time_percentage", self.__class__, i))

            sections.append(GlobalSpeedValidator.Section(lim.time_percentage, lim.distance_percentage))

        self._sections = np.array(sections)
        self._sections_times = np.array([s.time_percentage for s in sections])


