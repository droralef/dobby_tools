"""

Validator for minimal/maximal global speed

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import numpy as np
import numbers
from enum import Enum

import dobbyt
from dobbyt.movement import ValidationAxis

class GlobalSpeedValidator(dobbyt._Dobby_Object):
    """
    Validate minimal/maximal movement speed.
    The validation is of the *average* speed per trial. The validator can also interpolate the speed limit,
    i.e., impose the limit on the average speed from time=0 until any time point during the trial.
    """

    class SectionConfig(object):
        def __init__(self, to_time, min_speed=None, max_speed=None):
            self.to_time = to_time
            self.min_speed = min_speed
            self.max_speed = max_speed


    #-----------------------------------------------------------------------------------
    def __init__(self, active=False, sections=(), interpolate=True, axis=ValidationAxis.y):

        super(GlobalSpeedValidator, self).__init__()



    #========================================================================
    #      Validation API
    #========================================================================




    #========================================================================
    #      Config
    #========================================================================

    _errmsg_set_to_non_numeric = "dobbyt error: invalid attempt to set InstantaneousSpeedValidator.{0} to a non-numeric value ({1})"
    _errmsg_set_to_non_positive = "dobbyt error: invalid attempt to set InstantaneousSpeedValidator.{0} to a non-positive value ({1})"
    _errmsg_set_to_negative = "dobbyt error: invalid attempt to set InstantaneousSpeedValidator.{0} to a negative value ({1})"
    _errmsg_set_to_non_boolean = "dobbyt error: invalid attempt to set InstantaneousSpeedValidator.{0} to a non-boolean value ({1})"

    #-----------------------------------------------------------------------------------
    @property
    def active(self):
        """Whether the validator is currently active"""
        return self._active

    @active.setter
    def active(self, value):
        """
        Determine whether the validator is currently active
        :param value: Boolean
        """

        if not isinstance(value, bool):
            raise AttributeError(GlobalSpeedValidator._errmsg_set_to_non_boolean.format("active", value))

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

        # if value == ValidationAxis.x:
        #     self._calc_speed_func = GlobalSpeedValidator._calc_speed_x
        # elif value == ValidationAxis.y:
        #     self._calc_speed_func = GlobalSpeedValidator._calc_speed_y
        # elif value == ValidationAxis.xy:
        #     self._calc_speed_func = GlobalSpeedValidator._calc_speed_xy
        # else:
        #     raise AttributeError("dobbyt error: invalid value ({0}) for GlobalSpeedValidator.axis - expecting a value of type ValidationAxis".format(value))

        self._axis = value

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
            raise AttributeError(GlobalSpeedValidator._errmsg_set_to_non_numeric.format("grace_period", value))
        if value < 0:
            raise AttributeError(GlobalSpeedValidator._errmsg_set_to_negative.format("grace_period", value))

        self._grace_period = value

