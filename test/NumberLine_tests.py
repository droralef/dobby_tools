import unittest

from trajtracker.stimuli import NumberLine


class NumberLineTestCase(unittest.TestCase):

    #-- Create a NumberLine object, test default values
    def test_default_propertie(self):
        nl = NumberLine((10,20), 1000, 100)
        self.assertEqual(nl.position[0], 10)
        self.assertEqual(nl.position[1], 20)
        self.assertEqual(nl.min_value, 0)
        self.assertEqual(nl.max_value, 100)
        self.assertEqual(nl.line_length, 1000)
        self.assertEqual(nl.orientation, NumberLine.Orientation.Horizontal)


    #-- Validate() should fail when min>max
    def test_invalid_min_max(self):
        nl = NumberLine((10,20), 1000, min_value=100, max_value=100)
        self.assertRaises(ValueError, lambda: nl.validate())

    #-- Validate() should fail when some data is missing
    def test_missing_labels(self):
        nl = NumberLine((10,20), 1000, 100)
        nl.labels_visible = True
        self.assertRaises(ValueError, lambda: nl.validate())

        nl.show_labels(box_size=(10,10), font_name='Arial', font_size=3, font_colour=1)
        nl.validate()


    #----------- Validate update_xy()

    #-- Touch mode = undirectioned, horizontal line
    def test_touch_line_undirectioned_horizontal(self):
        nl = NumberLine((0,0), 100, 100, orientation=NumberLine.Orientation.Horizontal)
        nl.touch_directioned = False
        nl.touch_distance = 10

        #-- touch twice from the same direction
        nl.reset()
        self.assertFalse(nl.update_xy(0, 11))
        self.assertTrue(nl.update_xy(0, 9))

        #-- touch twice from two different directions
        nl.reset()
        self.assertFalse(nl.update_xy(0, 11))
        self.assertTrue(nl.update_xy(0, -9))


    #-- Touch mode = undirectioned, vertical line
    def test_touch_line_undirectioned_vertical(self):
        nl = NumberLine((0,0), 100, 100, orientation=NumberLine.Orientation.Vertical)
        nl.touch_directioned = False
        nl.touch_distance = 10

        #-- touch twice from the same direction
        nl.reset()
        self.assertFalse(nl.update_xy(11, 0))
        self.assertTrue(nl.update_xy(9, 0))

        #-- touch twice from two different directions
        nl.reset()
        self.assertFalse(nl.update_xy(11, 0))
        self.assertTrue(nl.update_xy(-9, 0))

    #-- Touch mode = directioned, horizontal line
    def test_touch_line_directioned_horizontal(self):
        nl = NumberLine((0,0), 100, 100, orientation=NumberLine.Orientation.Horizontal)
        nl.touch_directioned = True
        nl.touch_distance = 10

        #-- Get closer to the line
        nl.reset()
        self.assertFalse(nl.update_xy(0, 11))
        self.assertTrue(nl.update_xy(0, 9))

        #-- Cross the line
        nl.reset()
        self.assertFalse(nl.update_xy(0, 11))
        self.assertTrue(nl.update_xy(0, -100))

        #--- Now, from the other direction

        #-- Get closer to the line
        nl.reset()
        self.assertFalse(nl.update_xy(0, -11))
        self.assertTrue(nl.update_xy(0, -9))

        #-- Cross the line
        nl.reset()
        self.assertFalse(nl.update_xy(0, -11))
        self.assertTrue(nl.update_xy(0, 100))


    #-- Touch mode = directioned, vertical line
    def test_touch_line_directioned_vertical(self):
        nl = NumberLine((0,0), 100, 100, orientation=NumberLine.Orientation.Vertical)
        nl.touch_directioned = True
        nl.touch_distance = 10

        #-- Get closer to the line
        nl.reset()
        self.assertFalse(nl.update_xy(11, 0))
        self.assertTrue(nl.update_xy(9, 0))

        #-- Cross the line
        nl.reset()
        self.assertFalse(nl.update_xy(11, 0))
        self.assertTrue(nl.update_xy(-100, 0))

        #--- Now, from the other direction

        #-- Get closer to the line
        nl.reset()
        self.assertFalse(nl.update_xy(-11, 0))
        self.assertTrue(nl.update_xy(-9, 0))

        #-- Cross the line
        nl.reset()
        self.assertFalse(nl.update_xy(-11, 0))
        self.assertTrue(nl.update_xy(100, 0))


    #-- Touch mode = directioned, negative distance
    def test_touch_line_directioned_negative_distance(self):
        nl = NumberLine((0,0), 100, 100, orientation=NumberLine.Orientation.Horizontal)
        nl.touch_directioned = True
        nl.touch_distance = -10

        #-- Get closer to the line
        nl.reset()
        self.assertFalse(nl.update_xy(0, 10))
        self.assertFalse(nl.update_xy(0, 1))
        self.assertFalse(nl.update_xy(0, 0))
        self.assertFalse(nl.update_xy(0, -5))
        self.assertTrue(nl.update_xy(0, -11))




if __name__ == '__main__':
    unittest.main()
