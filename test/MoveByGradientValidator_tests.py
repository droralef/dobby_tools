import unittest

from dobbyt.validators import MoveByGradientValidator, ValidationFailed

grad = [[(0, 0, i) for i in range(0,100)]]



class MoveByGradientValidatorTests(unittest.TestCase):

    #-------------------------------------------------------
    def test_set_pos(self):
        val = MoveByGradientValidator(grad)

        val.position = (1, 1)
        val.position = (-1, -1)

        try:
            val.position = ""
        except ValueError:
            pass

        try:
            val.position = 1
        except ValueError:
            pass

        try:
            val.position = ("", "")
        except ValueError:
            pass

        try:
            val.position = (0.1, 0)
        except ValueError:
            pass

    #-------------------------------------------------------
    def test_set_enabled(self):
        val = MoveByGradientValidator(grad)

        val.enabled = True

        try:
            val.enabled = 1
        except ValueError:
            pass

        try:
            val.enabled = None
        except ValueError:
            pass


    # -------------------------------------------------------
    def test_set_last_validated_rgb(self):
        val = MoveByGradientValidator(grad)

        val.last_validated_rgb = (0, 0, 50)
        val.last_validated_rgb = 50

        try:
            val.last_validated_rgb = (-1, 0, 50)
        except ValueError:
            pass

        try:
            val.last_validated_rgb = (0, 0, 256)
        except ValueError:
            pass

        try:
            val.last_validated_rgb = (1.5, 0, 50)
        except ValueError:
            pass

        try:
            val.last_validated_rgb = ("", 0, 50)
        except ValueError:
            pass

        try:
            val.last_validated_rgb = (0, 0)
        except ValueError:
            pass

        try:
            val.last_validated_rgb = -1
        except ValueError:
            pass

        try:
            val.last_validated_rgb = 65536
        except ValueError:
            pass

        try:
            val.last_validated_rgb = ""
        except ValueError:
            pass

        try:
            val.last_validated_rgb = None
        except ValueError:
            pass


    # -------------------------------------------------------
    def test_set_max_valid_back_movement(self):
        val = MoveByGradientValidator(grad)

        val.max_valid_back_movement = 0
        val.max_valid_back_movement = 200

        try:
            val.max_valid_back_movement = None
        except ValueError:
            pass

        try:
            val.max_valid_back_movement = -1
        except ValueError:
            pass

        try:
            val.max_valid_back_movement = ""
        except ValueError:
            pass


    # -------------------------------------------------------
    def test_set_rgb_should_ascend(self):
        val = MoveByGradientValidator(grad)
        val.rgb_should_ascend = True

        try:
            val.rgb_should_ascend = 0
        except ValueError:
            pass

        try:
            val.rgb_should_ascend = None
        except ValueError:
            pass


    #-------------------------------------------------------
    def test_validate_basic(self):
        val = MoveByGradientValidator(grad, enabled=True)
        self.assertIsNone(val.check_xy(0, 0))
        self.assertIsNone(val.check_xy(10, 0))
        self.assertIsNotNone(val.check_xy(9, 0))


    #-------------------------------------------------------
    def test_validator_disabled(self):
        val = MoveByGradientValidator(grad)
        self.assertIsNone(val.check_xy(0, 0))
        self.assertIsNone(val.check_xy(-1, 0))


    #-------------------------------------------------------
    def test_validate_out_of_range(self):
        val = MoveByGradientValidator(grad, enabled=True)
        self.assertIsNone(val.check_xy(0, 0))
        self.assertIsNone(val.check_xy(-100, 0))


    #-------------------------------------------------------
    def test_validate_small_back_movement(self):
        val = MoveByGradientValidator(grad, enabled=True)
        val.max_valid_back_movement = 3
        self.assertIsNone(val.check_xy(0, 0))
        self.assertIsNone(val.check_xy(-3, 0))
        self.assertIsNotNone(val.check_xy(-4, 0))


    # -------------------------------------------------------
    def test_validate_descending(self):
        val = MoveByGradientValidator(grad, enabled=True, rgb_should_ascend=False)
        self.assertIsNone(val.check_xy(0, 0))
        self.assertIsNone(val.check_xy(-10, 0))
        self.assertIsNotNone(val.check_xy(-9, 0))


    #-------------------------------------------------------
    def test_validate_cross_zero(self):
        val = MoveByGradientValidator(grad, enabled=True, last_validated_rgb=(0, 0, 90))
        self.assertIsNone(val.check_xy(0, 0))   # the color here is 50
        self.assertIsNone(val.check_xy(40, 0))  # the color here is 90
        self.assertIsNone(val.check_xy(45, 0))  # the color here is 95
        self.assertIsNone(val.check_xy(-45, 0))  # the color here is 5

        val = MoveByGradientValidator(grad, enabled=True, last_validated_rgb=(0, 0, 90))
        self.assertIsNone(val.check_xy(0, 0))   # the color here is 50
        self.assertIsNone(val.check_xy(39, 0))  # the color here is 89
        self.assertIsNotNone(val.check_xy(-45, 0))



if __name__ == '__main__':
    unittest.main()
