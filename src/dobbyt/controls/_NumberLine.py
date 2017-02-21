"""

Number line: The NumberLine class presents a number line, detect when finger/mouse crosses it, and where

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from enum import Enum
import numbers
import numpy as np

from expyriment.misc import geometry
from expyriment.misc._timer import get_time
import expyriment.stimuli

import dobbyt


# noinspection PyAttributeOutsideInit,PyProtectedMember
class NumberLine(dobbyt._Dobby_Object):
    """
     A class that plots a number line and monitors its behavior.

     Visual features:
     - Plot a number line, horizontal or vertical
     - Optional tick marks at the end of the line and in locations along the line
     - Optional text labels at the end of the line
     - Allow modifying all common properties of the line and the text labels

     Behavioral features:
     - Detect when the finger/mouse clicks or crosses the number line
     - Support both the physical coordinate space and the logical position on the line

    """

    Orientation = Enum('Orientation', 'horizontal vertical')

    #===================================================================================
    #      Constructor + easy setters
    #===================================================================================

    def __init__(self, position, line_length, max_value, min_value=0,
                 orientation=Orientation.horizontal,
                 line_width=1, line_colour=None, end_tick_height=None,
                 visible=True):
        """
        Create a NumberLine object.

        :type line_length: number
        :type line_colour: tuple
        :type line_width: number
        :type min_value: number
        :type max_value: number
        :type end_tick_height: number

        :param position: the (x,y) coordinates of the middle of the line
        :param orientation: NumberLine.Orientation.horizontal or NumberLine.Orientation.vertical
        :param line_length: the length of the line, in pixels
        :param line_width: the width (thickness) of the line, in pixels (default = 1)
        :param line_colour: the color of the line (default = None)
        :param end_tick_height: the height of the ticks at the end of the line (default = None; see property for details)

        :param min_value: the logical value at the beginning of the line (default = 0)
        :param max_value: the logical value at the end of the line

        :param visible: set the line as visible/invisible in the next plotting
        """

        #-- The object starts as unlocked,but is locked when it is first drawn.
        #-- Locking means that its visual properties cannot be changed any longer
        self._locked = False

        self.orientation = orientation

        #-- Visual properties of the line itself
        self.position = position
        self.line_length = line_length
        self.line_width = line_width
        self.line_colour = line_colour
        self.end_tick_height = end_tick_height

        #-- Visual properties of the text labels at the ends of the line
        self.show_labels(visible=False)

        #-- Mid-of-line ticks

        #-- Logical length of the number line
        self.min_value = min_value
        self.max_value = max_value

        #-- Touch
        self._touch_directioned = True  # True: finger must be dragged to the NL from its initial direction
                                        # False: whenever the finger is close enough to the line, it's a touch
        self._touch_distance = 0        # Issue a "touch" decision when the finger is closer than this to the line
                                        # _touch_directioned=True and distance<0 means that finger must cross the line and get this far on the other side

        self.visible = visible

        self._visual_objects = {}

        self.reset_mouse_pos()



    #-----------------------------------------------------------------------------------
    def show_labels(self, visible=True, box_size=None, font_name=None, font_size=None, font_colour=None, offset=(0, 0),
                    text_min=None, text_max=None):
        """
        Determine appearance of the two text labels at the ends of the line

        :param visible: Whether the labels are visible or not (boolean)
        :param box_size: Size of the text box in pixels (width, height)
        :param font_name: Name of font
        :param font_size: Size of font
        :param font_colour: Color of font
        :param offset: (x,y) offset of a label (in pixels) relatively to the corresponding end of the number line
        :param text_min: Text for the label at the MIN end of the number line (default: min value)
        :param text_max: Text for the label at the MAX end of the number line (default: max value)
        """

        self.labels_visible = visible
        self.labels_box_size = box_size
        self.labels_font_colour = font_colour
        self.labels_font_name = font_name
        self.labels_font_size = font_size
        self.labels_offset = offset
        self.label_min_text = text_min
        self.label_max_text = text_max


    #===================================================================================
    #      Plotting
    #===================================================================================

    def preload(self):
        """
        Pre-load the number line - prepare for plotting
        :return: The time it took to run this function
        """

        start_time = get_time()

        if self._locked:
            # Already pre-loaded
            return int((get_time() - start_time) * 1000)

        self.validate()
        self._locked = True

        #-- Create the canvas for this number line
        self._prepare_canvas()

        if self._line_colour is not None:
            self._prepare_main_line()
            if self._end_tick_height != 0 and self._end_tick_height is not None:
                self._prepare_end_of_line_ticks()

        if self._labels_visible:
            self._prepare_labels()

        #-- Plot all visual elements on the canvas
        for k in self._visual_objects:
            self._visual_objects[k].plot(self._canvas)

        return int((get_time() - start_time) * 1000)


    #-------------------------------------------------------
    def _prepare_canvas(self):

        self._canvas_to_nl_coord_shift = (0, 0)

        #-- First, get the minimal/maximal coordinates of elements on the canvas

        # Start and end of the number line
        xmin, ymin = self._main_line_start()
        xmax, ymax = self._main_line_end()

        # Apply tick marks
        if self._orientation == NumberLine.Orientation.horizontal:
            ymax += self.end_tick_height
        else:
            xmax += self.end_tick_height

        # Apply text labels
        if self._labels_visible:

            text_x_offset_min = self._labels_offset_x - self._labels_box_size[0]/2
            text_x_offset_max = self._labels_offset_x + self._labels_box_size[0]/2

            text_y_offset_min = self._labels_offset_y - self._labels_box_size[1]/2
            text_y_offset_max = self._labels_offset_y + self._labels_box_size[1]/2

            xmin = min(xmin, xmin + text_x_offset_min)
            xmax = max(xmax, xmax + text_x_offset_max)
            ymin = min(ymin, ymin + text_y_offset_min)
            ymax = max(ymax, ymax + text_y_offset_max)

        #-- In order to keep the number line's center in coordinates (0,0), i.e., in the center of the
        #-- canvas, make sure the canvas is symmetric
        #-- Get canvas size
        width = 2 * max(xmax, -xmin)
        height = 2 * max(ymax, -ymin)

        #-- Create the canvas
        self._canvas = expyriment.stimuli.Canvas(size=(width, height), colour=None)


    #-------------------------------------------------------
    def _prepare_main_line(self):
        main_line = expyriment.stimuli.Line(self._main_line_start(), self._main_line_end(),
                                            self._line_width, self._line_colour)
        main_line.preload()

        # print "preparing line from {0} to {1} width={2} color={3}".format(self._main_line_start(), self._main_line_end(), self._line_width, self._line_colour)

        self._visual_objects['main_line'] = main_line

    #-------------------------------------------------------
    def _prepare_end_of_line_ticks(self):
        tick_dx = 0 if self._orientation == NumberLine.Orientation.horizontal else self._end_tick_height
        tick_dy = self._end_tick_height if self._orientation == NumberLine.Orientation.horizontal else 0

        pt1 = self._main_line_start()
        pt2 = self._main_line_end()
        tick1 = expyriment.stimuli.Line(pt1, (pt1[0] + tick_dx, pt1[1] + tick_dy),
                                        self._line_width, self._line_colour)
        tick2 = expyriment.stimuli.Line(pt2, (pt2[0] + tick_dx, pt2[1] + tick_dy),
                                        self._line_width, self._line_colour)

        tick1.preload()
        tick2.preload()

        self._visual_objects['endtick1'] = tick1
        self._visual_objects['endtick2'] = tick2


    #-------------------------------------------------------
    # Text labels - one at each end of the line
    #
    def _prepare_labels(self):
        dx = self._labels_offset_x
        dy = self._labels_offset_y

        min_text = str(self._min_value) if self._label_min_text is None else self._label_min_text
        min_pos = self._main_line_start()
        min_pos = (min_pos[0] + dx, min_pos[1] + dy)
        min_box = expyriment.stimuli.TextBox(text=min_text, size=self._labels_box_size, position=min_pos,
                                             text_font=self._labels_font_name, text_colour=self._labels_font_colour,
                                             text_size=self._labels_font_size, text_justification=1)  # 1=center
        min_box.preload()

        max_text = str(self._max_value) if self._label_max_text is None else self._label_max_text
        max_pos = self._main_line_end()
        max_pos = (max_pos[0] + dx, max_pos[1] + dy)
        max_box = expyriment.stimuli.TextBox(text=max_text, size=self._labels_box_size, position=max_pos,
                                             text_font=self._labels_font_name, text_colour=self._labels_font_colour,
                                             text_size=self._labels_font_size, text_justification=1)  # 1=center
        max_box.preload()

        self._visual_objects['label_min'] = min_box
        self._visual_objects['label_max'] = max_box

        return

    #-------------------------------------------------------
    # Get start/end points of the main line relatively to the canvas
    #
    def _main_line_start(self):
        if self._orientation == NumberLine.Orientation.horizontal:
            return -self._line_length/2, 0
        else:
            return 0, -self._line_length/2


    def _main_line_end(self):
        if self._orientation == NumberLine.Orientation.horizontal:
            return self._line_length/2, 0
        else:
            return 0, self._line_length/2


    #-------------------------------------------------------
    def plot(self, stimulus):
        """
        Plot all number line elements in a container canvas and return it
        :param stimulus: The stimulus to plot on
        :return: The time (in ms) it took this function to run
        """

        start_time = get_time()

        self.preload()

        self._canvas.position = (self._mid_x, self._mid_y)
        self._canvas.plot(stimulus)

        return int((get_time() - start_time)*1000)


    #===================================================================================
    #      Track movement
    #===================================================================================

    _errmsg_mouseat_non_numeric_coord = "dobbyt error in NumberLine.mouseAt(): a non-numeric {0} coordinate was provided ({1})"

    #---------------------------------------------------------
    def reset_mouse_pos(self):
        """
        Reset the last-known mouse position, so that mouse_at() will forget any previous movement
        This function is typically called in the beginning of a trial.
        """

        self._last_mouse_coord = None    # Last coordinate where mouse was observed (x or y, depending on the number line orientation)
        self._last_touched_coord = None  # Last coordinate where the number line was touched (x or y, depending on the number line orientation)
        self._initial_mouse_dir = None   # +1 or -1: indicates the first click position relatively to the number line


    #---------------------------------------------------------
    def mouse_at(self, xCoord, yCoord):
        """
        This function is called when mouse/touch has moved. It checks whether the movement implies touching the number line.
        :param xCoord:
        :param yCoord:
        :return: True if the number line was touched
        """
        if not isinstance(xCoord, numbers.Number):
            raise AttributeError(NumberLine._errmsg_mouseat_non_numeric_coord.format("x", xCoord))
        if not isinstance(yCoord, numbers.Number):
            raise AttributeError(NumberLine._errmsg_mouseat_non_numeric_coord.format("y", xCoord))

        if self._last_touched_coord is not None:
            return False

        #-- Get the relevant coordinates (x or y)
        if self._orientation == NumberLine.Orientation.horizontal:
            mouse_coord = yCoord
            line_coord = self._main_line_start()[1]
        else:
            mouse_coord = xCoord
            line_coord = self._main_line_start()[0]

        distance = line_coord - mouse_coord  # positive value: mouse coord < line coord

        if not self._touch_directioned:
            #-- Direction doesn't matter. Just check the distance from the number line.
            touched = np.abs(distance) <= self._touch_distance

        elif self._initial_mouse_dir is None:
            #-- Finger must approach the line from its initial direction, which was not set: set it now
            self._initial_mouse_dir = np.sign(distance)
            touched = False

        else:
            # Fix sign of distance, such that distance>0 means that the finger is still approaching the number line
            distance *= self._initial_mouse_dir

            touched = distance < self._touch_distance

        return touched


    #---------------------------------------------------------
    def last_touched_coord(self):
        """
        The coordinate where the mouse/finger last touched the number line.
        This is either the x or y coordinate, depending on the number line orientation
        If the finger didn't touch the line since the last call to reset_mouse_pos(), the function returns None.
        """
        return self._last_touched_coord


    #---------------------------------------------------------
    def last_touched_value(self):
        """
        The position where the mouse/finger last touched the number line.
        The value returned is in the number line's scale.
        If the finger didn't touch the line since the last call to reset_mouse_pos(), the function returns None.
        """
        if self._last_touched_coord is None:
            return None

        #-- Convert the coordinate into a position using a 0-1 scale
        s = self._main_line_start()
        s_coord = s[0] if self._orientation == NumberLine.Orientation.horizontal else s[1]
        pos01 = (self._last_touched_coord - s_coord) / self.line_length

        # noinspection PyUnresolvedReferences
        return pos01 * (self._max_value - self._min_value) + self._min_value

    #===================================================================================
    #      Property setters / getters
    #===================================================================================

    _errmsg_set_to_non_numeric = "dobbyt error: invalid attempt to set NumberLine.{0} to a non-numeric value ({1})"
    _errmsg_set_to_non_positive = "dobbyt error: invalid attempt to set NumberLine.{0} to a non-positive value ({1})"
    _errmsg_set_to_non_boolean = "dobbyt error: invalid attempt to set NumberLine.{0} to a non-boolean value ({1})"
    _errmsg_set_to_non_string = "dobbyt error: invalid attempt to set NumberLine.{0} to a non-string value ({1})"

    _errmsg_value_not_collection = "dobbyt error: invalid value for NumberLine.{0} ({1}) - expecting a tuple or list"
    _errmsg_value_bad_length = "dobbyt error: invalid value for NumberLine.{0} ({1}) - expecting a 2-element tuple"
    _errmsg_set_to_non_numeric_entry = "dobbyt error: invalid value for NumberLine.{0} - {2} is not a number ({1})"
    _errmsg_set_to_non_positive_entry = "dobbyt error: invalid value for NumberLine.{0} - {2} is a non-positive number({1})"

    #-----------------------------------------------------------
    def validate(self):
        """
        Validate that the number line configuration is ok.
        Raises an AttributeError if not.
        """

        if self._min_value >= self._max_value:
            raise AttributeError("dobbyt error: NumberLine.min_value({0}) >= NumberLine.max_value({1})".format(self._min_value, self._max_value))

        if self._labels_visible:
            if self._labels_box_size is None:
                raise AttributeError("dobbyt error: NumberLine - labels textbox size was not specified")
            if self._labels_font_name is None or self._labels_font_name == "":
                raise AttributeError("dobbyt error: NumberLine - labels font name was not specified")
            if self._labels_font_size is None:
                raise AttributeError("dobbyt error: NumberLine - labels font size was not specified")
            if self._labels_font_colour is None:
                raise AttributeError("dobbyt error: NumberLine - labels font color was not specified")



    #-----------------------------------------------------------
    def _validate_unlocked(self):
        if self._locked:
            raise dobbyt.InvalidStateError('An attempt was made to change the visual properties of a NumberLine after it was already plotted')

    ###################################
    #  Line properties
    ###################################


    #-----------------------------------------------------------
    @property
    def orientation(self):
        """Get the number line's orientation (horizontal / vertical) """
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        """
        Set the number line orientation
        :param value: NLOrientation.horizontal or NLOrientation.vertical
        """

        self._validate_unlocked()

        if not isinstance(value, dobbyt.controls.NumberLine.Orientation):
            raise AttributeError("dobbyt error: invalid value for NumberLine.orientation ({0}) - expecting NumberLine.Orientation.horizontal or NumberLine.Orientation.vertical".format(value))

        self._orientation = value

    #-----------------------------------------------------------
    @property
    def position(self):
        """
        Get the number line's position: the (x,y) coordinates of the line mid point
        """
        return self._mid_x, self._mid_y

    @position.setter
    def position(self, value):
        """
        Set the number line position: coordinates of its mid point
        :param value: an (x,y) tuple/list
        """

        self._validate_unlocked()

        if isinstance(value, geometry.XYPoint):
            self._mid_x = value.x
            self._mid_y = value.y
            return

        if not hasattr(value, '__iter__'):
            raise AttributeError(NumberLine._errmsg_value_not_collection.format("position", value))
        if len(value) != 2:
            raise AttributeError(NumberLine._errmsg_value_bad_length.format("position", value))
        if not isinstance(value[0], numbers.Number):
            raise AttributeError(NumberLine._errmsg_set_to_non_numeric_entry.format("position", value, "x coordinate"))
        if not isinstance(value[1], numbers.Number):
            raise AttributeError(NumberLine._errmsg_set_to_non_numeric_entry.format("position", value, "y coordinate"))

        self._mid_x = value[0]
        self._mid_y = value[1]

    #-----------------------------------------------------------
    @property
    def line_length(self):
        """Get the number line length (in pixels)"""
        return self._line_length

    @line_length.setter
    def line_length(self, value):
        """
        Set the number line physical length
        :param value: only positive value, specified in pixels.
        """

        self._validate_unlocked()

        if not isinstance(value, numbers.Number):
            raise AttributeError(NumberLine._errmsg_set_to_non_numeric.format("line_length", value))
        if value <= 0:
            raise AttributeError(NumberLine._errmsg_set_to_non_positive.format("line_length", value))

        self._line_length = value

    #-----------------------------------------------------------
    @property
    def end_tick_height(self):
        """Get the height of the ticks at the ends of the number line (in pixels)"""
        return self._end_tick_height

    @end_tick_height.setter
    def end_tick_height(self, value):
        """
        Set the height of the ticks at the ends of the number line (in pixels).
        :param value: positive values = ticks above the line or to its right; negative values = below/left
        """

        self._validate_unlocked()

        if value is not None and not isinstance(value, numbers.Number):
            raise AttributeError(NumberLine._errmsg_set_to_non_numeric.format("end_tick_height", value))

        self._end_tick_height = value

    #-----------------------------------------------------------
    @property
    def line_width(self):
        """Get the number line width (in pixels)"""
        return self._line_width

    @line_width.setter
    def line_width(self, value):
        """
        Set the number line width
        :param value: only positive value, specified in pixels.
        """

        self._validate_unlocked()

        if not isinstance(value, numbers.Number):
            raise AttributeError(NumberLine._errmsg_set_to_non_numeric.format("line_width", value))
        if value <= 0:
            raise AttributeError(NumberLine._errmsg_set_to_non_positive.format("line_width", value))

        self._line_width = value

    #-----------------------------------------------------------
    @property
    def line_colour(self):
        """Get the color of the number line. None = line not plotted."""
        return self._line_colour

    @line_colour.setter
    def line_colour(self, value):
        """Set the number line color. None = the line will not be plotted."""

        self._validate_unlocked()
        self._line_colour = value


    ###################################
    #  Labels properties
    ###################################

    #-----------------------------------------------------------
    @property
    def labels_visible(self):
        """Return True/False to indicate whether the end-of-line labels are visible"""
        return self._labels_visible

    @labels_visible.setter
    def labels_visible(self, value):
        """Set the end-of-line labels as visible or invisible. Expecting a boolean/number argument."""
        if isinstance(value, numbers.Number):
            value = value != 0
        elif not isinstance(value, bool):
                raise AttributeError(NumberLine._errmsg_set_to_non_boolean, "labels_visible", value)

        self._labels_visible = value

    #-----------------------------------------------------------
    @property
    def labels_font_name(self):
        """Get the font name of the end-of-line labels"""
        return self._labels_font_name

    @labels_font_name.setter
    def labels_font_name(self, value):
        """Get the font name of the end-of-line labels."""

        self._validate_unlocked()

        if value is not None and type(value) != str:
            raise AttributeError(NumberLine._errmsg_set_to_non_string.format("labels_font_name", value))

        self._labels_font_name = value

    #-----------------------------------------------------------
    @property
    def labels_font_colour(self):
        """Get the font color of the end-of-line labels."""
        return self._labels_font_colour

    @labels_font_colour.setter
    def labels_font_colour(self, value):
        """Set the font color of the end-of-line labels."""

        self._validate_unlocked()
        self._labels_font_colour = value


    #-----------------------------------------------------------
    @property
    def labels_font_size(self):
        """Get the font size of the end-of-line labels"""
        return self._labels_font_size

    @labels_font_size.setter
    def labels_font_size(self, value):
        """
        Set the font size of the end-of-line labels
        :param value: only positive value.
        """

        self._validate_unlocked()

        if value is not None:
            if not isinstance(value, numbers.Number):
                raise AttributeError(NumberLine._errmsg_set_to_non_numeric.format("labels_font_size", value))
            if value <= 0:
                raise AttributeError(NumberLine._errmsg_set_to_non_positive.format("labels_font_size", value))

        self._labels_font_size = value


    #-----------------------------------------------------------
    @property
    def labels_box_size(self):
        """Get the textbox size of the end-of-line labels (height, width)"""
        return self._labels_box_size

    @labels_box_size.setter
    def labels_box_size(self, value):
        """
        Set the textbox size of the end-of-line labels
        :param value: height, width
        """

        self._validate_unlocked()

        if value is not None:
            if not hasattr(value, '__iter__'):
                raise AttributeError(NumberLine._errmsg_value_not_collection.format("labels_box_size", value))
            if len(value) != 2:
                raise AttributeError(NumberLine._errmsg_value_bad_length.format("labels_box_size", value))
            if not isinstance(value[0], numbers.Number):
                raise AttributeError(NumberLine._errmsg_set_to_non_numeric_entry.format("labels_box_size", value, "height"))
            if not isinstance(value[1], numbers.Number):
                raise AttributeError(NumberLine._errmsg_set_to_non_numeric_entry.format("labels_box_size", value, "width"))
            if value[0] <= 0:
                raise AttributeError(NumberLine._errmsg_set_to_non_positive_entry.format("labels_box_size", value, "height"))
            if value[1] <= 0:
                raise AttributeError(NumberLine._errmsg_set_to_non_positive_entry.format("labels_box_size", value, "width"))

        self._labels_box_size = value

    #-----------------------------------------------------------
    @property
    def labels_offset(self):
        """
        Get the number line's position: the (x,y) coordinates of the line mid point
        """
        return self._labels_offset_x, self._labels_offset_y

    @labels_offset.setter
    def labels_offset(self, value):
        """
        Set the number line position: coordinates of its mid point
        :param value: an (x,y) tuple/list
        """

        self._validate_unlocked()

        if isinstance(value, geometry.XYPoint):
            self._labels_offset_x = value.x
            self._labels_offset_y = value.y
            return

        if not hasattr(value, '__iter__'):
            raise AttributeError(NumberLine._errmsg_value_not_collection.format("labels_offset", value))
        if len(value) != 2:
            raise AttributeError(NumberLine._errmsg_value_bad_length.format("labels_offset", value))
        if not isinstance(value[0], numbers.Number):
            raise AttributeError(NumberLine._errmsg_set_to_non_numeric_entry.format("labels_offset", value, "x"))
        if not isinstance(value[1], numbers.Number):
            raise AttributeError(NumberLine._errmsg_set_to_non_numeric_entry.format("labels_offset", value, "y"))

        self._labels_offset_x = value[0]
        self._labels_offset_y = value[1]

    #-----------------------------------------------------------
    @property
    def label_min_text(self):
        """Get the text for the label at the MIN end of the number line"""
        return self._label_min_text

    @label_min_text.setter
    def label_min_text(self, value):
        """Set the text for the label at the MIN end of the number line"""

        self._validate_unlocked()

        if isinstance(value, numbers.Number):
            value = str(value)
        elif value is not None and type(value) != str:
            raise AttributeError(NumberLine._errmsg_set_to_non_string.format("label_min_text", value))

        self._label_min_text = value

    #-----------------------------------------------------------
    @property
    def label_max_text(self):
        """Get the text for the label at the MAX end of the number line"""
        return self._label_max_text

    @label_max_text.setter
    def label_max_text(self, value):
        """Set the text for the label at the MAX end of the number line"""

        self._validate_unlocked()

        if isinstance(value, numbers.Number):
            value = str(value)
        elif value is not None and type(value) != str:
            raise AttributeError(NumberLine._errmsg_set_to_non_string.format("label_max_text", value))

        self._label_max_text = value




    ###################################
    #  Line values
    ###################################

    #-----------------------------------------------------------
    @property
    def min_value(self):
        """Get the minimal logical value on the number line"""
        return self._min_value

    @min_value.setter
    def min_value(self, value):
        """Set the minimal logical value on the number line"""

        if not isinstance(value, numbers.Number):
            raise AttributeError(NumberLine._errmsg_set_to_non_numeric.format("min_value", value))

        self._min_value = value

    #-----------------------------------------------------------
    @property
    def max_value(self):
        """Get the maximal logical value on the number line"""
        return self._max_value

    @max_value.setter
    def max_value(self, value):
        """Set the maximal logical value on the number line"""

        self._validate_unlocked()

        if not isinstance(value, numbers.Number):
            raise AttributeError(NumberLine._errmsg_set_to_non_numeric.format("max_value", value))

        self._max_value = value


    #-----------------------------------------------------------
    @property
    def visible(self):
        """Return True/False to indicate whether the number line is visible"""
        return self._visible

    @visible.setter
    def visible(self, value):
        """Set the number line as visible or invisible. Expecting a boolean/number argument."""
        if isinstance(value, numbers.Number):
            value = value != 0
        elif not isinstance(value, bool):
                raise AttributeError(NumberLine._errmsg_set_to_non_boolean, "visible", value)

        self._visible = value


    ###################################
    #  Touch properties
    ###################################

    #-----------------------------------------------------------
    @property
    def touch_distance(self):
        """Minimal distance from line that counts as touch (negative value: finger must cross to the other side)"""
        return self._touch_distance

    @touch_distance.setter
    def touch_distance(self, value):
        """Set the minimal distance from line that counts as touch """

        self._validate_unlocked()

        if not isinstance(value, numbers.Number):
            raise AttributeError(NumberLine._errmsg_set_to_non_numeric.format("touch_distance", value))

        self._touch_distance = value


    #-----------------------------------------------------------
    @property
    def touch_directioned(self):
        """Whether the number line can be touched only from the finger's movement direction (True) or from any direction (False)"""
        return self._touch_directioned

    @touch_directioned.setter
    def touch_directioned(self, value):

        self._validate_unlocked()

        if not isinstance(value, numbers.Number):
            raise AttributeError(NumberLine._errmsg_set_to_non_boolean.format("touch_directioned", value))

        self._touch_directioned = value


