"""

Dobby tools - movement package - utilities

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
