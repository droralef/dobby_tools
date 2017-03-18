"""

 Allow mouse to be only in specific pixels, as defined by a BMP file

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import dobbyt

from dobbyt.misc import LocationColorMap
from dobbyt.misc._utils import BaseValidator, ErrMsg
from dobbyt.validators import ValidationFailed

import dobbyt.misc.utils as u



class LocationsValidator(BaseValidator):

    err_invalid_coordinates = "invalid_coords"


    def __init__(self, image, top_left_coord=None, default_valid=False):
        """
        Constructor
        :param image: Name of a BMP file, or the actual image (rectangular matrix of colors)
        :param top_left_coord: See :func:`~dobbyt.movement.LocationsValidator.top_left_coord`
        :param default_valid: See :func:`~dobbyt.movement.LocationsValidator.default_valid`
        """
        super(LocationsValidator, self).__init__()

        self._lcm = LocationColorMap(image, top_left_coord=top_left_coord, use_mapping=True, colormap="RGB")
        self.default_valid = default_valid
        self.valid_colors = set()
        self.invalid_colors = set()


    #======================================================================
    #   Properties
    #======================================================================

    #-------------------------------------------------
    @property
    def top_left_coord(self):
        """
        The top-left coordinate of the image provided in the constructor
        The coordinate should be an (x,y) tuple/list
        If top_left_coord=(a,b), then :func:`~dobbyt.misc.LocationColorMap.get_color_at`(a,b) will return the
        color of the top-left point of the image
        """
        return self._lcm.top_left_coord

    @top_left_coord.setter
    def top_left_coord(self, value):
        self._lcm.top_left_coord = value


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
            raise AttributeError(ErrMsg.attr_invalid_type(type(self), attr_name, "iterable", value))

        colors = set()
        for c in value:
            if not u.is_rgb(c):
                raise AttributeError(ErrMsg.attr_invalid_type(type(self), attr_name, "color", value))
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

        color = self._lcm.get_color_at(x_coord, y_coord)
        if self._default_valid:
            ok = color not in self._invalid_colors
        else:
            ok = color in self._valid_colors

        if not ok:
            raise ValidationFailed(self.err_invalid_coordinates, "You moved to an invalid location", self)


