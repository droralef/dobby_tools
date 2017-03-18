"""

 Given a BMP image, translate a coordinate into the color code in that coordinate.

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from scipy import misc
import numbers

import dobbyt
from dobbyt.misc._utils import BaseValidator, ErrMsg
from dobbyt.misc.utils import color_rgb_to_num


# noinspection PyAttributeOutsideInit
class LocationColorMap(dobbyt._Dobby_Object):
    """
    Translate the finger location into a code, according to a BMP image
    """

    #-------------------------------------------------
    def __init__(self, image, top_left_coord=None, use_mapping=False, colormap=None):
        """
        Constructor
        :param image: Name of a BMP file, or the actual image (rectangular matrix of colors)
        :param top_left_coord: See :func:`~dobbyt.misc.LocationColorMap.top_left_coord`
        :param use_mapping: See :func:`~dobbyt.misc.LocationColorMap.use_mapping`
        :param colormap: See :func:`~dobbyt.misc.LocationColorMap.colormap`
        """

        super(LocationColorMap, self).__init__()

        if isinstance(image, list) and isinstance(image[0], list):
            self._image = image
            self._filename = None
        else:
            self._image = misc.imread(image, mode='RGB')
            self._filename = image

        self._height = len(self._image)
        self._width = len(self._image[0])

        self._to_tuples()
        self._find_available_colors()

        self.top_left_coord = top_left_coord
        self.colormap = colormap
        self._use_mapping = use_mapping


    #-------------------------------------------------
    def _find_available_colors(self):

        self._available_colors = set()

        for row in self._image:
            for cell in row:
                self._available_colors.add(cell)


    # -------------------------------------------------
    def _to_tuples(self):

        self._image = list(self._image)
        for row in range(len(self._image)):
            self._image[row] = list(self._image[row])
            for col in range(len(self._image[0])):
                self._image[row][col] = tuple(self._image[row][col])


    #-------------------------------------------------
    @property
    def top_left_coord(self):
        """
        The top-left coordinate of the image provided in the constructor
        The coordinate should be an (x,y) tuple/list
        If top_left_coord=(a,b), then :func:`~dobbyt.misc.LocationColorMap.get_color_at`(a,b) will return the
        color of the top-left point of the image.
        """
        return self._top_left_coord

    @top_left_coord.setter
    def top_left_coord(self, value):

        if value is None:
            value = (0, 0)

        if not isinstance(value, (list, tuple)):
            raise ValueError("dobbyt error: invalid {0}.top_left_coord ({1})".format(self.__class__, value))

        if not isinstance(value[0], numbers.Number):
            raise ValueError("dobbyt error: invalid {0}.top_left_coord[0] ({1})".format(self.__class__, value[0]))

        if not isinstance(value[1], numbers.Number):
            raise ValueError("dobbyt error: invalid {0}.top_left_coord[1] ({1})".format(self.__class__, value[1]))


        self._top_left_coord = (value[0], value[1])


    #-------------------------------------------------
    @property
    def use_mapping(self):
        """
        The default value of the 'use_mapping' argument in get_color_at()
        """
        return self._use_mapping

    @use_mapping.setter
    def use_mapping(self, value):
        if not isinstance(value, bool):
            raise ValueError(ErrMsg.attr_invalid_type(self.__class__, "use_mapping", "bool", value))
        self._use_mapping = value


    #-------------------------------------------------
    @property
    def available_colors(self):
        """
        Return a set with all colors that exist in the image
        """
        return frozenset(self._available_colors)

    #-------------------------------------------------
    @property
    def colormap(self):
        """
        Mapping of each color in the image to another value. This mapping will be used when calling get_color_at(use_mapping=True)

        Valid values:
        - None (default): no mapping; calling get_color_at(use_mapping=True)
        - "RGB": Each color is assigned the RGB code - a number between 0 and 65535 (0xFFFFFF)
        - "DEFAULT": Each color is assigned a unique code (0, 1, 2, etc.). Codes are assigned by order of RGB codes.
        - or a dictionary that maps each color in the image (RGB tuple) to a value
        """
        return self._color_to_code

    @colormap.setter
    def colormap(self, value):

        if value is None:
            #-- No mapping: use default colors
            self._color_to_code = None

        elif isinstance(value, str) and value.lower() == "default":
            #-- Use arbitrary coding
            self._color_to_code = {}
            n = 0
            for color in sorted(list(self._available_colors)):
                self._color_to_code[color] = n
                n += 1

        elif isinstance(value, str) and value.lower() == "rgb":
            # Translate each triplet to an RGB code
            self._color_to_code = {}
            for color in self._available_colors:
                self._color_to_code[color] = color_rgb_to_num(color)

        elif isinstance(value, dict):
            #-- Use this mapping; but make sure that all colors from the image were defined
            missing_colors = set()
            for color in self._available_colors:
                if color not in value:
                    missing_colors.add(color)
            if len(missing_colors) > 0:
                raise ValueError("dobbyt error: Invalid value for {0}.color_codes - some colors are missing: {1}".format(self.__class__, missing_colors))

            self._color_to_code = value.copy()

        else:
            raise ValueError(
                "dobbyt error: {0}.color_codes can only be set to None, 'default', or a dict. Invalid value: {1}".format(
                    self.__class__, value))


    #-------------------------------------------------
    def get_color_at(self, x_coord, y_coord, use_mapping=None):
        """
        Return the color at a given coordinate
        :param x_coord:
        :param y_coord:
        :param use_mapping:
        :return: The color in the given place, or None if the coordinate is out of the image range
        """

        if not isinstance(x_coord, int):
            raise ValueError(ErrMsg.invalid_method_arg_type(self.__class__, "get_color_at", "int", "x_coord", x_coord))
        if not isinstance(y_coord, int):
            raise ValueError(ErrMsg.invalid_method_arg_type(self.__class__, "get_color_at", "int", "y_coord", y_coord))

        if use_mapping is None:
            use_mapping = self._use_mapping
        elif not isinstance(use_mapping, bool):
            raise ValueError(ErrMsg.invalid_method_arg_type(self.__class__, "get_color_at", "bool", "use_mapping", use_mapping))

        if self._color_to_code is None and use_mapping:
            raise ValueError("dobbyt error: a call to %s.get_color_at(use_mapping=True) is invalid because color_codes were not specified" % self.__class__)

        if x_coord < self._top_left_coord[0] or x_coord >= self._top_left_coord[0]+self._width or \
               y_coord < self._top_left_coord[1] or y_coord >= self._top_left_coord[1] + self._height:
            return None

        x_coord -= self._top_left_coord[0]
        y_coord -= self._top_left_coord[1]

        v = self._image[y_coord][x_coord]

        return self._color_to_code[v] if use_mapping else v
