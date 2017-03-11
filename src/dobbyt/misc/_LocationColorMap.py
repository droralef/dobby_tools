"""

 Translate the finger location into a code, according to a BMP image

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from scipy import misc
import numbers

import dobbyt
from dobbyt.movement._utils import BaseValidator


class LocationColorMap(dobbyt._Dobby_Object):
    """
    Translate the finger location into a code, according to a BMP image
    """

    #-------------------------------------------------
    def __init__(self, img_filename, top_left_coord=(0, 0)):
        """
        :param img_filename: Name of a BMP file
        """
        super(LocationColorMap, self).__init__()

        self._image = misc.imread(img_filename, mode='RGB')
        self._filename = img_filename
        self._height = len(self._image)
        self._width = len(self._image[0])

        self.top_left_coord = top_left_coord

        self._to_tuples()
        self._find_available_colors()


    #-------------------------------------------------
    def _find_available_colors(self):

        self._values_to_codes = {}
        n = 0

        for row in self._image:
            for cell in row:
                if cell not in self._values_to_codes:
                    self._values_to_codes[cell] = n
                    n += 1


    #-------------------------------------------------
    def _recode(self):

        self._find_available_colors()
        for row in range(len(self._image)):
            for col in range(len(self._image[0])):
                v = self._image[row][col]
                self._image[row][col] = self._values_to_codes[v]


    # -------------------------------------------------
    def _to_tuples(self):

        self._image = list(self._image)
        for row in range(len(self._image)):
            self._image[row] = list(self._image[row])
            for col in range(len(self._image[0])):
                self._image[row][col] = tuple(self._image[row][col])


    #-------------------------------------------------
    @property
    def available_colors(self):
        return tuple(self._values_to_codes)

    #-------------------------------------------------
    @property
    def top_left_coord(self):
        return self._top_left_coord

    @top_left_coord.setter
    def top_left_coord(self, value):

        if not isinstance(value, (list, tuple)):
            raise ValueError("dobbyt error: invalid {0}.top_left_coord ({1})".format(type(self), value))

        if not isinstance(value[0], numbers.Number):
            raise ValueError("dobbyt error: invalid {0}.top_left_coord[0] ({1})".format(type(self), value[0]))

        if not isinstance(value[1], numbers.Number):
            raise ValueError("dobbyt error: invalid {0}.top_left_coord[1] ({1})".format(type(self), value[1]))


        self._top_left_coord = (value[0], value[1])


    #-------------------------------------------------
    def get_color_at(self, x_coord, y_coord, as_code=False):
        """
        Return the color at a given coordinate
        :param x_coord:
        :param y_coord:
        :return: The color in the given place, or None if the coordinate is out of the image range
        """

        if not isinstance(x_coord, int):
            raise ValueError(BaseValidator._errmsg_non_numeric_func_arg.format(type(self), "get_color_at", "int", "x_coord", x_coord))
        if not isinstance(y_coord, int):
            raise ValueError(BaseValidator._errmsg_invalid_func_arg_type.format(type(self), "get_color_at", "int", "y_coord", y_coord))

        if x_coord < self._top_left_coord[0] or x_coord >= self._top_left_coord[0]+self._width or \
            y_coord < self._top_left_coord[1] or y_coord >= self._top_left_coord[1] + self._height:
            return None

        v = self._image[y_coord][x_coord]

        return self._values_to_codes[v] if as_code else v
