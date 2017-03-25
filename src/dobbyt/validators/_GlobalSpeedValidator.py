"""

Validator for minimal/maximal global speed

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

from enum import Enum
import numbers
import numpy as np

import expyriment as xpy

import dobbyt
import dobbyt._utils as _u
from dobbyt.validators import ValidationAxis, ValidationFailed, _BaseValidator
from dobbyt.movement import StimulusAnimator


# noinspection PyAttributeOutsideInit
class GlobalSpeedValidator(_BaseValidator):
    """
    Validate minimal movement speed.
    The validation is of the *average* speed per trial. The validator can also interpolate the speed limit,
    i.e., impose the limit on the average speed from time=0 until any time point during the trial.
    """

    err_too_slow = "too_slow"

    arg_expected_coord = "expected_coord"
    arg_actual_coord = "actual_coord"


    class Section(object):
        def __init__(self, time_percentage, distance_percentage):
            self.time_percentage = time_percentage
            self.distance_percentage = distance_percentage

        def __str__(self):
            return "GlobalSpeedValidator.Section(time={:}, distance={:})".format(self.time_percentage, self.distance_percentage)


    #-----------------------------------------------------------------------------------
    def __init__(self, enabled=False, origin_coord=None, end_coord=None, axis=ValidationAxis.y,
                 grace_period=None, max_trial_duration=None, sections=None, show_guide=False):
        """

        :param enabled: See :func:`dobbyt.validators.GlobalSpeedValidator.enabled`
        :type enabled: bool

        :param origin_coord: See :func:`dobbyt.validators.GlobalSpeedValidator.origin_coord`
        :type origin_coord: int

        :param end_coord: See :func:`dobbyt.validators.GlobalSpeedValidator.end_coord`
        :type end_coord: int

        :param axis: See :func:`dobbyt.validators.GlobalSpeedValidator.axis`
        :type axis: dobbyt.validators.ValidationAxis

        :param grace_period: See :func:`dobbyt.validators.GlobalSpeedValidator.grace_period`
        :type grace_period: number

        :param max_trial_duration: See :func:`dobbyt.validators.GlobalSpeedValidator.max_trial_duration`
        :type max_trial_duration: number

        :param sections: See :func:`dobbyt.validators.GlobalSpeedValidator.sections`
        :type sections: list of GlobalSpeedValidator.Section objects

        :param show_guide: See :func:`dobbyt.validators.GlobalSpeedValidator.show_guide`
        :type show_guide: bool
        """

        super(GlobalSpeedValidator, self).__init__(enabled=enabled)

        self.axis = axis
        self.grace_period = grace_period

        if sections is None:
            self.sections = [self.Section(1, 1)]
        else:
            self.sections = sections

        self._max_trial_duration = None
        if max_trial_duration is not None:
            self.max_trial_duration = max_trial_duration

        self._origin_coord = None
        if origin_coord is not None:
            self.origin_coord = origin_coord

        self._end_coord = None
        if end_coord is not None:
            self.end_coord = end_coord

        self.show_guide = show_guide
        self.guide_line_length = None


    #========================================================================
    #      Validation API
    #========================================================================

    #----------------------------------------------------------------------------------
    def reset(self, time0=0):
        """
        Called when a trial starts - reset any previous movement

        :param time0: The time when the trial started
        :type time0: number
        """

        if time0 is not None and not isinstance(time0, (int, float)):
            raise ValueError(_u.ErrMsg.invalid_method_arg_type(self.__class__, "reset", "numeric", "time", time0))

        self._time0 = time0


    #----------------------------------------------------------------------------------
    def check_xyt(self, x_coord, y_coord, time):
        """
        Validate movement.

        :param x_coord:
        :type x_coord: int

        :param y_coord:
        :type y_coord: int

        :param time: Time from start of trial
        :returns: None if all OK; ValidationFailed object if error
        """

        self._check_xyt_validate_and_log(x_coord, y_coord, time)
        self._assert_initialized(self._origin_coord, "origin_coord")
        self._assert_initialized(self._end_coord, "end_coord")
        self._assert_initialized(self._max_trial_duration, "max_trial_duration")

        if not self._enabled:
            return None

        #-- If this is the first call in a trial: do nothing
        if self._time0 is None:
            self.reset(time)
            return None

        if time < self._time0:
            raise dobbyt.InvalidStateError("{0}.check_xyt() was called with time={1}, but the trial started at time={2}".format(self.__class__, time, self._time0))

        time -= self._time0

        #-- Get the expected and actual coordinates
        coord = x_coord if self._axis == ValidationAxis.x else y_coord
        expected_coord = int(self.get_expected_coord_at_time(time))
        d_coord = coord - expected_coord

        #-- No validation during grace period
        if time <= self._grace_period:
            if self._show_guide:
                self._guide.show(expected_coord, GlobalSpeedGuide.LineMode.Grace)
            return None

        #-- Actual coordinate must be ahead of the expected minimum
        if d_coord != 0 and np.sign(d_coord) != np.sign(self._end_coord - self._origin_coord):
            return self._create_validation_error(self.err_too_slow, "You moved too slowly",
                                                 {self.arg_expected_coord: expected_coord, self.arg_actual_coord: coord})

        if self._show_guide:
            # Get the coordinate that the mouse/finger should reach shortly
            coord_expected_soon = self.get_expected_coord_at_time(time + self._guide_warning_time_delta)

            # check if mouse/finger already reached this coordinate
            reached_expected_soon = d_coord == 0 or np.sign(coord - coord_expected_soon) == np.sign(self._end_coord - self._origin_coord)

            # set guide color accordingly
            self._guide.show(expected_coord, GlobalSpeedGuide.LineMode.OK if reached_expected_soon else GlobalSpeedGuide.LineMode.Error)

        return None

    def _assert_initialized(self, value, attr_name):
        if value is None:
            raise dobbyt.InvalidStateError("{:}.check_xyt() was called before {:} was initalized".format(type(self).__name__, attr_name))

    #----------------------------------------------------------------------------------
    # Get the coordinate expected
    #
    def get_expected_coord_at_time(self, time):
        """
        Return the minimnal coordinate (x or y, depending on axis) that should be obtained in a given time
        """

        total_distance = self._end_coord - self._origin_coord

        remaining_time = time
        result = self._origin_coord
        for section in self._sections:
            section_duration = section.time_percentage * self._max_trial_duration
            section_distance = section.distance_percentage * total_distance
            if remaining_time > section_duration:
                remaining_time -= section_duration
                result += section_distance
            else:
                result += section_distance * (remaining_time / section_duration)
                break

        return result

    #========================================================================
    #      Configure
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
        _u.validate_attr_type(self, "axis", value, ValidationAxis)
        if value == ValidationAxis.xy:
            raise ValueError(_u.ErrMsg.attr_invalid_value(self.__class__, "axis", value))

        self._axis = value
        self._log_setter("axis")

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
        _u.validate_attr_numeric(self, "origin_coord", value, _u.NoneValues.Invalid)
        self._origin_coord = value
        self._log_setter("origin_coord")

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
        _u.validate_attr_numeric(self, "end_coord", value, _u.NoneValues.Invalid)
        self._end_coord = value
        self._log_setter("end_coord")


    #-----------------------------------------------------------------------------------
    @property
    def grace_period(self):
        """The grace period in the beginning of each trial, during which speed is not validated (in seconds)."""
        return self._grace_period

    @grace_period.setter
    def grace_period(self, value):
        value = _u.validate_attr_numeric(self, "grace_period", value, _u.NoneValues.ChangeTo0)
        _u.validate_attr_not_negative(self, "grace_period", value)
        self._grace_period = value
        self._log_setter("grace_period")

    #-----------------------------------------------------------------------------------
    @property
    def max_trial_duration(self):
        """The maximal duration of a trial (in seconds)."""
        return self._max_trial_duration

    @max_trial_duration.setter
    def max_trial_duration(self, value):
        value = _u.validate_attr_numeric(self, "max_trial_duration", value, _u.NoneValues.ChangeTo0)
        _u.validate_attr_positive(self, "max_trial_duration", value)
        self._max_trial_duration = value
        self._log_setter("max_trial_duration")

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

        _u.validate_attr_type(self, "sections", value, (list, tuple))

        total_time = 0
        total_distance = 0

        sections = []
        for i in range(len(value)):
            section = value[i]

            _u.validate_attr_type(self, "sections[{:}]".format(i), section, (GlobalSpeedValidator.Section, tuple, list))

            if not isinstance(section, GlobalSpeedValidator.Section):
                #-- convert tuple/list to section
                if len(section) != 2:
                    raise ValueError("dobbyt error: {:}.section[{:}] should be either a Section object or a (time,distance) tuple/list. Invalid value: {:}".format(type(self).__name__, i, section))
                section = GlobalSpeedValidator.Section(section[0], section[1])

            if not isinstance(section.distance_percentage, numbers.Number):
                raise ValueError(GlobalSpeedValidator._errmsg_sections_not_percentage.format("distance_percentage", type(self).__name__, i))
            if not (0 < section.distance_percentage <= 1):
                raise ValueError(GlobalSpeedValidator._errmsg_sections_not_percentage.format("distance_percentage", type(self).__name__, i))

            if not isinstance(section.time_percentage, numbers.Number):
                raise ValueError(GlobalSpeedValidator._errmsg_sections_not_percentage.format("time_percentage", type(self).__name__, i))
            if not (0 < section.time_percentage <= 1):
                raise ValueError(GlobalSpeedValidator._errmsg_sections_not_percentage.format("time_percentage", type(self).__name__, i))
            if section.distance_percentage <= total_distance:
                raise ValueError("dobbyt error: {:}.sections[{:}] is invalid - the distance specified ({:}) must be later than in the previous section".format("distance_percentage", type(self).__name__, i, section.time_percentage))

            total_time += section.time_percentage
            total_distance += section.distance_percentage

            if total_time > 1:
                raise ValueError("dobbyt error: {:}.sections is invalid - the total time of all sections exceeds 1.0".format(type(self).__name__))
            if total_distance > 1:
                raise ValueError("dobbyt error: {:}.sections is invalid - the total distance of all sections exceeds 1.0".format(type(self).__name__))

            sections.append(GlobalSpeedValidator.Section(section.time_percentage, section.distance_percentage))

        if total_time < 1:
            raise ValueError(
                "dobbyt error: {:}.sections is invalid - the total time of all sections sums to {:} rather than to 1.0".format(
                    type(self).__name__, total_time))
        if total_distance < 1:
            raise ValueError(
                "dobbyt error: {:}.sections is invalid - the total distance of all sections sums to {:} rather than to 1.0".format(
                    type(self).__name__, total_distance))

        self._sections = np.array(sections)
        self._sections_times = np.array([s.time_percentage for s in sections])


    #-------------------------------------------------------------
    @property
    def show_guide(self):
        """ Whether to visualize the speed limit as a moving line """
        return self._show_guide

    @show_guide.setter
    def show_guide(self, show):
        _u.validate_attr_type(self, "show_guide", show, bool)
        self._show_guide = show

    #-------------------------------------------------------------
    @property
    def guide_warning_time_delta(self):
        """
        If the time difference between the mouse/finger current coordinate and the required coordinate is
        less than this value, the visual line guide will change its color.
        """
        return self._guide_warning_time_delta

    @guide_warning_time_delta.setter
    def guide_warning_time_delta(self, value):
        _u.validate_attr_type(self, "guide_warning_time_delta", value, numbers.Number)
        _u.validate_attr_not_negative(self, "guide_warning_time_delta", value)
        self._guide_warning_time_delta = value

    #-------------------------------------------------------------
    @property
    def guide_line_length(self):
        """
        The length of the speed guide line
        """
        return self._guide_line_length

    @guide_line_length.setter
    def guide_line_length(self, value):
        _u.validate_attr_type(self, "guide_line_length", value, numbers.Number, none_allowed=True)
        if value is not None:
            _u.validate_attr_positive(self, "guide_line_length", value)
        self._guide_line_length = value
        self._guide = GlobalSpeedGuide(self)

    #-------------------------------------------------------------
    @property
    def guide(self):
        """
        A :class:`dobbyt.validators.GlobalSpeedGuide` that takes care of showing a visual guide for the speed limit
        (read-only property)
        """
        return self._guide



#==========================================================================================
# Show a moving line to visualize the validator's speed
#==========================================================================================

class GlobalSpeedGuide(dobbyt._DobbyObject):
    """
    This class displays a moving line that visualizes the global speed limit.

    """

    LineMode = Enum("LineMode", "Grace OK Error")


    def __init__(self, validator):
        """
        Constructor

        :param validator: See :class:`dobbyt.validators.GlobalSpeedValidator`
        """

        super(GlobalSpeedGuide, self).__init__()
        self._validator = validator

        self._initialized = False
        self._guide_line = None

        self.line_width = 1
        self.colour_grace = (255, 255, 255)
        self.colour_ok = (0, 255, 0)
        self.colour_err = (255, 0, 0)
        self.visible = False

        self._initialized = True
        self._create_guide_line()


    #--------------------------------------------------
    def _create_guide_line(self):

        if not self._initialized:
            return

        line_length = self._get_line_length()
        if line_length is None:
            return

        if self._validator.axis == ValidationAxis.x:
            start_pt = (0, -line_length/2)
            end_pt = (0, line_length/2)
        else:
            start_pt = (-line_length/2, 0)
            end_pt = (line_length/2, 0)

        self._guide_line = dobbyt.stimuli.StimulusSelector()
        self._guide_line.add_stimulus(self.LineMode.Grace, self._create_line(start_pt, end_pt, self._colour_grace))
        self._guide_line.add_stimulus(self.LineMode.Error, self._create_line(start_pt, end_pt, self._colour_err))
        self._guide_line.add_stimulus(self.LineMode.OK, self._create_line(start_pt, end_pt, self._colour_ok))

    #--------------------------------------------------
    def _get_line_length(self):
        if self._validator.guide_line_length is not None:
            return self._validator.guide_line_length
        elif xpy._active_exp.screen is None:
            return None
        elif self._validator.axis == ValidationAxis.x:
            return xpy._active_exp.screen.size[1]
        else:
            return xpy._active_exp.screen.size[0]

    #--------------------------------------------------
    def _create_line(self, start_pt, end_pt, color):
        line = xpy.stimuli.Line(start_point=start_pt, end_point=end_pt, line_width=self._line_width, colour=color)
        line.preload()
        return line


    #=====================================================================================
    #    Runtime API
    #=====================================================================================


    #------------------------------------------------------------------------
    def show(self, coord, line_mode):
        if self._guide_line is None:
            self._create_guide_line()  # try creating again. Maybe the experiment was inactive
            if self._guide_line is None:
                raise dobbyt.InvalidStateError("The visual guide for {:} cannot be created because the experiment is inactive".format(GlobalSpeedValidator.__name__))

        _u.validate_func_arg_type(self, "show", "coord", coord, int)
        _u.validate_func_arg_type(self, "show", "line_mode", line_mode, self.LineMode)

        self._guide_line.select(line_mode)

        pos = (coord, 0) if self._validator.axis == ValidationAxis.x else (0, coord)
        self._guide_line.position = pos
        self._guide_line.present(clear=False, update=False)


    #=====================================================================================
    #    Configure
    #=====================================================================================

    #-------------------------------------------------------
    @property
    def visible(self):
        """ Whether the speed guide is currently visible or not """
        return self._visible

    @visible.setter
    def visible(self, value):
        _u.validate_attr_type(self, "visible", value, bool)
        self._visible = value

    #-------------------------------------------------------
    @property
    def colour_grace(self):
        """ The guiding line's color during the validator's grace period """
        return self._colour_grace

    @colour_grace.setter
    def colour_grace(self, value):
        _u.validate_attr_rgb(self, "colour_grace", value)
        self._colour_grace = value
        self._create_guide_line()

    #--------------------------
    @property
    def colour_ok(self):
        """ The guiding line's color when the mouse/finger is moving properly """
        return self._colour_ok

    @colour_ok.setter
    def colour_ok(self, value):
        _u.validate_attr_rgb(self, "colour_ok", value)
        self._colour_ok = value
        self._create_guide_line()

    #--------------------------
    @property
    def colour_err(self):
        """ The guiding line's color when the mouse/finger is moving an invalid speed """
        return self._colour_err

    @colour_err.setter
    def colour_err(self, value):
        _u.validate_attr_rgb(self, "colour_err", value)
        self._colour_err = value
        self._create_guide_line()

    #-------------------------------------------------------
    @property
    def line_width(self):
        """ The guiding line's width """
        return self._line_width

    @line_width.setter
    def line_width(self, value):
        _u.validate_attr_type(self, "line_width", value, int)
        self._line_width = value
        self._create_guide_line()
