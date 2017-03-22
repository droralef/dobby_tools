import unittest


from dobbyt.misc import ShapeMap


class ShapeMapTests(unittest.TestCase):


    #====================================================================
    # Configure
    #====================================================================

    #-------------------------------------------------
    def test_set_pos(self):
        sm = ShapeMap()
        sm.position = (1, 1)
        sm.position = [2, 3]
        sm.position = None
        self.assertEqual((0, 0), sm.position)

        try:
            sm.position = ""
            self.fail()
        except ValueError:
            pass

        try:
            sm.position = 0
            self.fail()
        except ValueError:
            pass

        try:
            sm.position = (None, 0)
            self.fail()
        except ValueError:
            pass

        try:
            sm.position = (0, None)
            self.fail()
        except ValueError:
            pass

    #-------------------------------------------------
    def test_set_rotation(self):
        sm = ShapeMap()

        sm.rotation = None
        sm.rotation = -10

        try:
            sm.rotation = ""
            self.fail()
        except ValueError:
            pass

    #--------------------------------------------------
    def test_add_shape(self):
        sm = ShapeMap()
        sm.add_shape(ShapeMap.Circle(0, 0, 10), "a")
        self.assertRaises(ValueError, lambda: sm.add_shape("z", "a"))

    #--------------------------------------------------
    def test_set_shapes(self):
        sm = ShapeMap()
        sm.shapes = [(ShapeMap.Circle(0, 0, 10), "a"), [ShapeMap.Circle(0, 0, 10), "b"]]
        sm.shapes = []

        try:
            sm.shapes = ""
            self.fail()
        except ValueError:
            pass

        try:
            sm.shapes = [(1)]
            self.fail()
        except ValueError:
            pass

        try:
            sm.shapes = [""]
            self.fail()
        except ValueError:
            pass


    #====================================================================
    # Get shapes
    #====================================================================

    #--------------------------------------------------
    def test_get_shape(self):
        sm = ShapeMap()
        shape_a = ShapeMap.Circle(0, 0, 10)
        shape_b = ShapeMap.Circle(20, 20, 10)
        sm.shapes = [(shape_a, "a"), [shape_b, "b"]]

        self.assertEqual("a", sm.get_shape_at(5, 5))
        self.assertEqual(shape_a, sm.get_shape_at(5, 5, return_shape_id=False))

        self.assertEqual("b", sm.get_shape_at(20, 15))
        self.assertEqual(shape_b, sm.get_shape_at(20, 15, return_shape_id=False))

        self.assertIsNone(sm.get_shape_at(0, 30))
        self.assertIsNone(sm.get_shape_at(0, 30, return_shape_id=False))

    #--------------------------------------------------
    def test_get_shape_with_overlap(self):
        sm = ShapeMap()
        shape_a = ShapeMap.Circle(0, 0, 10)
        shape_b = ShapeMap.Circle(0, 0, 10)
        sm.shapes = [(shape_a, "a"), [shape_b, "b"]]

        self.assertEqual("a", sm.get_shape_at(5, 5))


    #--------------------------------------------------
    def test_get_shape_with_rotation(self):
        sm = ShapeMap(rotation=90)
        sm.shapes = [(ShapeMap.Circle(0, 20, 10), "a")]

        self.assertEqual("a", sm.get_shape_at(20, 0))  # rotated position
        self.assertIsNone(sm.get_shape_at(0, 20))      # unrotated position



if __name__ == '__main__':
    unittest.main()
