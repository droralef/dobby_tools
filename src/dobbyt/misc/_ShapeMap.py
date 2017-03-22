"""

 Given a coordinate, find the shape in that position

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import numbers

import numpy as np

import dobbyt
import dobbyt._utils as _u
import dobbyt.utils as u



class ShapeMap(dobbyt._DobbyObject):
    """
    Maintain a list of shapes, with coordinate for each.
    Given a specific coordinate, return the shape that overlaps that location.
    Each shape is assigned a logical ID (which can be any object). The class can return either the shape or its ID.
    """

    def __init__(self, position=(0, 0), rotation=0, shapes=None):
        """
        Constructor
        :param position: See :func:`~dobbyt.misc.ShapeMap.position`
        :param rotation: See :func:`~dobbyt.misc.ShapeMap.rotation`
        :param shapes: See :func:`~dobbyt.misc.ShapeMap.shapes`
        """
        super(ShapeMap, self).__init__()

        self.position = position
        self.rotation = rotation
        self.shapes = shapes



    #====================================================================================
    #  Configure
    #====================================================================================

    #-------------------------------------------------
    @property
    def shapes(self):
        """
        The shapes. A list/tuple of shape definition, each of which is a 2-element list/tuple with shape and ID.
        Shape: a shape object from the expyriment.stimuli package, a shape object defined as inner classes here,
          or any object that supports the overlapping_with_position() method.
        ID: Any object.
        """
        return list(self._shapes)

    @shapes.setter
    def shapes(self, value):
        if value == None:
            self._shapes = []
            return

        _u.validate_attr_type(self, "shapes", value, (list, tuple))

        self._shapes = []
        for shape in value:
            _u.validate_attr_type(self, "shapes[...]", shape, (list, tuple))
            if len(shape) != 2:
                raise ValueError("dobbyt error: invalid value for {0}.shapes - expecting a list of (shape, id) pairs")
            self.add_shape(shape[0], shape[1])


    def add_shape(self, shape, id):
        if 'overlapping_with_position' not in dir(shape):
            raise ValueError("dobbyt error: Invalid shape assigned to %s" % type(self).__name__)

        self._shapes.append((shape, id))


    #-------------------------------------------------
    @property
    def position(self):
        """
        The coordinate of the set of shapes - (x,y) tuple/list
        """
        return self._position

    @position.setter
    def position(self, value):

        if value is None:
            value = (0, 0)

        _u.validate_attr_type(self, "position", value, (list, tuple))
        _u.validate_attr_type(self, "position[0]", value[0], numbers.Number)
        _u.validate_attr_type(self, "position[1]", value[1], numbers.Number)

        self._position = (value[0], value[1])
        self._log_setter("position")

    #-------------------------------------------------
    @property
    def rotation(self):
        """
        The angle (degrees) by which the shape-map is rotated (positive=clockwise)
        """
        return self._rotation


    @rotation.setter
    def rotation(self, degrees):
        degrees = _u.validate_attr_numeric(self, "rotation", degrees, none_value=_u.NoneValues.ChangeTo0)
        self._rotation = degrees
        self._log_setter("rotation")


    #====================================================================================
    #  Find shape at location
    #====================================================================================

    def get_shape_at(self, x_coord, y_coord, return_shape_id=True):
        """
        Return the shape at the given position.
        If there are overlapping shapes, return the one that was defined first
        :param x_coord: Using the coordinate system of the ShapeMape
        :param y_coord: Using the coordinate system of the ShapeMape
        :param return_shape_id: If True (default), return the shape ID. If False, return the shape itself.
        :return: Shape/ID, or None if no shape was found in that position.
        """
        _u.validate_func_arg_type(self, "get_shape_at", "x_coord", x_coord, int)
        _u.validate_func_arg_type(self, "get_shape_at", "y_coord", y_coord, int)
        _u.validate_func_arg_type(self, "get_shape_at", "return_shape_id", return_shape_id, bool)

        pos = (x_coord - self._position[0], y_coord - self._position[1])
        pos = u.rotate_coord(pos, -self._rotation)

        for shape in self._shapes:
            if not shape[0].overlapping_with_position(pos):
                continue

            return shape[1] if return_shape_id else shape[0]

        return None


    #====================================================================================
    #  "Logical" shapes (so you don't have to use Expyriment shapes)
    #====================================================================================

    #----------------------------------------------------
    class Rectangle(object):

        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height


        def overlapping_with_position(self, pos):
            x, y = pos
            return x >= self.x and x <= self.x + self.width and \
                y >= self.y and y <= self.y + self.height


    #----------------------------------------------------
    class Circle(object):

        def __init__(self, x, y, radius):
            self.x = x
            self.y = y
            self.radius = radius

        def overlapping_with_position(self, pos):
            x, y = pos
            distance_from_center = np.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
            return distance_from_center <= self.radius
