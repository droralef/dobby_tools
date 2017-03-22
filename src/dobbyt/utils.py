"""

Dobby tools - movement package - public utilities

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division
from numpy import pi, arctan, cos, sin


#--------------------------------------------------------------------------
def get_angle(xy1, xy2, as_degrees=False):
    """
    Get the direction of finger movement, in radians. 0 = upwards.
    :param xy1: Coordinates in time point #1
    :param xy2: Coordinates in a later time point
    """

    dx = xy2[0] - xy1[0]
    dy = xy2[1] - xy1[1]

    if dx == 0:
        # up=0, down=pi
        angle = 0 if dy > 0 else pi

    elif dx > 0:
        # Right movement; return angles from 0 to pi
        angle = arctan(- dy / dx) + pi / 2

    else:
        # Left movement; return angles from pi to pi*2
        angle = arctan(- dy / dx) + pi * 3 / 2


    if as_degrees:
        angle *= 360 / (pi*2)

    return angle


#--------------------------------------------------------------------------
def color_rgb_to_num(rgb):
    """
    Convert an RGB color (3 integers, each 0-255) to a single int value (between 0 and 0xFFFFFF)
    """
    if not is_rgb(rgb):
        raise ValueError("dobbyt error: invalid argument to color_rgb_to_num(), expecting a 3*integer list/tuple")
    return (rgb[0]<<16) + (rgb[1]<<8) + rgb[2]


def is_rgb(rgb):
    """
    Check if the given value is a valid RGB color (3 integers, each 0-255)
    """
    return isinstance(rgb, (list, tuple)) and len(rgb) == 3 \
           and isinstance(rgb[0], int) and 0 <= rgb[0] <= 255 \
           and isinstance(rgb[1], int) and 0 <= rgb[1] <= 255 \
           and isinstance(rgb[2], int) and 0 <= rgb[2] <= 255



#--------------------------------------------------------------------------
def rotate_coord(coord, angle, origin=(0,0), is_radians=False):
    """
    Rotate the given coordinate about the origin
    :param coord: The x,y coordinate to rotate
    :param angle: The rotation angle (positive = clockwise)
    :param origin: The point to rotate around (default=0,0)
    :param is_radians: whether angle is provided as radians (True) or degrees (False)
    :return: The new x,y coordinates
    """

    if not is_radians:
        angle = angle / 360 * pi*2

    x = coord[0] - origin[0]
    y = coord[1] - origin[1]

    x1 = x * cos(angle) + y * sin(angle)
    y1 = y * cos(angle) - x * sin(angle)

    return x1 + origin[0], y1 + origin[1]
