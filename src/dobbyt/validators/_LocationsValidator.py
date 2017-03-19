"""

 Allow mouse to be only in specific pixels, as defined by a BMP file

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from dobbyt.misc import LocationColorMap
from dobbyt.misc._utils import BaseValidator, ErrMsg
from dobbyt.validators import ValidationFailed

import dobbyt.misc.utils as u



class LocationsValidator(BaseValidator):
    """
    This validator gets an image, and validates that the mouse/finger would be placed
    only on pixels of certain color(s).
    You can define either the valid colors or the invalid colors.
    """

    err_invalid_coordinates = "invalid_coords"

    def __init__(self, image, enabled=False, position=None, default_valid=False):
        """
        Constructor
        :param image: Name of a BMP file, or the actual image (rectangular matrix of colors)
        :param enabled: See :func:`~dobbyt.movement.LocationsValidator.enabled`
        :param position: See :func:`~dobbyt.movement.LocationsValidator.position`
        :param default_valid: See :func:`~dobbyt.movement.LocationsValidator.default_valid`
        """
        super(LocationsValidator, self).__init__(enabled=enabled)

        self._lcm = LocationColorMap(image, position=position, use_mapping=True, colormap="RGB")
        self.default_valid = default_valid
        self.valid_colors = set()
        self.invalid_colors = set()


    #======================================================================
    #   Properties
    #======================================================================

    #-------------------------------------------------
    @property
    def position(self):
        """
        The position of the image: (x,y) tuple/list, indicating the image center
        For even-sized images, use the Expyriment standard.
        The position is used to align the image's coordinate space with that of mouse_at()
        """
        return self._lcm.position

    @position.setter
    def position(self, value):
        self._lcm.position = value


    #-------------------------------------------------
    @property
    def default_valid(self):
        """
        Indicates whether by default, all points are valid or not.
        If True: use :func:`~dobbyt.misc.LocationColorMap.invalid_colors` to indicate exceptions
        If False: use :func:`~dobbyt.misc.LocationColorMap.valid_colors` to indicate exceptions
        """
        return self._default_valid


    @default_valid.setter
    def default_valid(self, value):
        self.validate_type(self, value, bool)
        self._default_valid = value


    #-------------------------------------------------
    @property
    def valid_colors(self):
        return self._valid_colors

    @valid_colors.setter
    def valid_colors(self, value):
        self._valid_colors = self._get_colors_as_ints(value, "valid_colors")


    @property
    def invalid_colors(self):
        return self._invalid_colors

    @invalid_colors.setter
    def invalid_colors(self, value):
        self._invalid_colors = self._get_colors_as_ints(value, "valid_colors")


    def _get_colors_as_ints(self, value, attr_name):
        if u.is_rgb(value):
            value = (value,)

        if not isinstance(value, (list, tuple, set)):
            raise ValueError(ErrMsg.attr_invalid_type(type(self), attr_name, "iterable", value))

        colors = set()
        for c in value:
            if not u.is_rgb(c):
                raise ValueError(ErrMsg.attr_invalid_type(type(self), attr_name, "color", value))
            colors.add(u.color_rgb_to_num(c))

        return colors


    #======================================================================
    #   Validate
    #======================================================================


    def mouse_at(self, x_coord, y_coord):
        """
        Check whether the given coordinate is a valid one
        :param x_coord: number
        :param y_coord: number
        """
        self.mouse_at_validate_xy(x_coord, y_coord)

        if not self._enabled:
            return

        color = self._lcm.get_color_at(x_coord, y_coord)
        if self._default_valid:
            ok = color not in self._invalid_colors
        else:
            ok = color in self._valid_colors

        if not ok:
            raise ValidationFailed(self.err_invalid_coordinates, "You moved to an invalid location", self)


