"""

Dobby tools - movement package - public utilities

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from numpy import pi, arctan


#--------------------------------------------------------------------------
def get_angle(xy1, xy2):
    """
    Get the direction of finger movement, in radians. 0 = upwards.
    :param xy1: Coordinates in time point #1
    :param xy2: Coordinates in a later time point
    """

    dx = xy2[0] - xy1[0]
    dy = xy2[1] - xy1[1]

    if dx == 0:
        # up=0, down=pi
        return 0 if dy > 0 else pi
    elif dx > 0:
        # Right movement; return angles from 0 to pi
        angle = arctan(- dy / dx) + pi / 2
    else:
        # Left movement; return angles from pi to pi*2
        angle = arctan(- dy / dx) + pi * 3 / 2

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

