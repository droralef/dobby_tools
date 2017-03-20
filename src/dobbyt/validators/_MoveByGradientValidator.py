"""

 Allow mouse to move only according to a given image - from light color to a darker color (or vice versa)

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numbers

import dobbyt._utils as _u
import dobbyt.misc.utils as u
from dobbyt.misc import LocationColorMap
from dobbyt.validators import ValidationFailed, _BaseValidator



class MoveByGradientValidator(_BaseValidator):
    """
    This validator gets an image, and allows mouse to move only according to it -
    from a light color to a darker color (or vice versa).
    """

    err_gradient = "gradient_violation"


    def __init__(self, image, position=None, rgb_should_ascend=True, max_valid_back_movement=0, last_validated_rgb=None,
                 enabled=False):
        """
        Constructor
        :param image: Name of a BMP file, or the actual image (rectangular matrix of colors)
        :param position: See :func:`~dobbyt.movement.MoveByGradientValidator.enabled`; default = False
        :param position: See :func:`~dobbyt.movement.MoveByGradientValidator.position`; default = (0,0)
        :param rgb_should_ascend: See :func:`~dobbyt.movement.MoveByGradientValidator.rgb_should_ascend`; default = True
        :param max_valid_back_movement: See :func:`~dobbyt.movement.MoveByGradientValidator.max_valid_back_movement`; default = 0
        :param last_validated_rgb: See :func:`~dobbyt.movement.MoveByGradientValidator.last_validated_rgb`; default = None
        """
        super(MoveByGradientValidator, self).__init__(enabled=enabled)

        self._lcm = LocationColorMap(image, position=position, use_mapping=True, colormap="RGB")
        self.rgb_should_ascend = rgb_should_ascend
        self.max_valid_back_movement = max_valid_back_movement
        self.last_validated_rgb = last_validated_rgb
        self.reset()


    #======================================================================
    #   Properties
    #======================================================================

    #-------------------------------------------------
    @property
    def position(self):
        """
        The position of the image: (x,y) tuple/list, indicating the image center
        For even-sized images, use the Expyriment standard.
        The position is used to align the image's coordinate space with that of check_xy()
        """
        return self._lcm.position

    @position.setter
    def position(self, value):
        self._lcm.position = value


    #-------------------------------------------------
    @property
    def rgb_should_ascend(self):
        """
        Whether the valid movement is from lower RGB codes to higher RGB codes (True) or vice versa (False)
        """
        return self._rgb_should_ascend


    @rgb_should_ascend.setter
    def rgb_should_ascend(self, value):
        _u.validate_attr_type(self, "rgb_should_ascend", value, bool)
        self._rgb_should_ascend = value


    #-------------------------------------------------
    @property
    def last_validated_rgb(self):
        """
        The last RGB color code to be validated (number between 0 and 65535; when assigning, you can also
        specify a list/tuple of 3 integers, each 0-255).
        If the last mouse position was on a color with RGB higher than this (or lower for rgb_should_ascend=False),
        validation is not done. This is intended to allow for "cyclic" movement, i.e., allow to "cross" the 0
        (e.g. from 0 to 65535 and then back to 0).
        Setting the value to None disables this feature
        """
        return self._last_validated_rgb


    @last_validated_rgb.setter
    def last_validated_rgb(self, value):
        if u.is_rgb(value):
            self._last_validated_rgb = u.color_rgb_to_num(value)
        else:
            if value is not None:
                _u.validate_attr_numeric(self, "last_validated_rgb", value)
                _u.validate_attr_not_negative(self, "last_validated_rgb", value)
            self._last_validated_rgb = value


    #-------------------------------------------------
    @property
    def max_valid_back_movement(self):
        """
        The maximal valid delta of color-change in the opposite direction that would still be allowed
        """
        return self._max_valid_back_movement


    @max_valid_back_movement.setter
    def max_valid_back_movement(self, value):
        _u.validate_attr_numeric(self, "max_valid_back_movement", value)
        _u.validate_attr_not_negative(self, "max_valid_back_movement", value)
        self._max_valid_back_movement = value



    #======================================================================
    #   Validate
    #======================================================================

    #-----------------------------------------------------------------
    def reset(self):
        """
        Reset the movement validation
        """
        self._last_color = None


    #-----------------------------------------------------------------
    def check_xy(self, x_coord, y_coord):
        """
        Validate the movement
        :return: None if all OK, ValidationFailed if error
        """
        _u.validate_func_arg_type(self, "check_xy", "x_coord", x_coord, numbers.Number)
        _u.validate_func_arg_type(self, "check_xy", "y_coord", y_coord, numbers.Number)

        if not self._enabled:
            return None

        color = self._lcm.get_color_at(x_coord, y_coord)
        if color is None:
            return None  # can't validate

        if self._last_color is None:
            #-- Nothing to validate
            self._last_color = color
            return None


        expected_direction = 1 if self._rgb_should_ascend else -1
        rgb_delta = (color - self._last_color) * expected_direction
        if rgb_delta >= 0:
            #-- All is OK
            self._last_color = color
            return None

        if rgb_delta >= -self._max_valid_back_movement:
            #-- The movement was in the opposite color diredction, but only slightly:
            #-- Don't issue an error, but also don't update "last_color" - remember the previous one
            return None

        #-- Invalid situation!

        if self._last_validated_rgb is not None and \
                ((self._rgb_should_ascend and self._last_color > self._last_validated_rgb) or
                 (not self._rgb_should_ascend and self._last_color < self._last_validated_rgb)):
            #-- Previous color is very close to 0 - avoid validating, in order to allow "crossing the 0 color"
            return None

        return ValidationFailed(self.err_gradient, "You moved in an invalid direction", self)


