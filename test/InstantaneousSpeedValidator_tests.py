import unittest


from dobbyt.validators import InstantaneousSpeedValidator, ValidationAxis, SpeedError, ValidationFailed



class InstantaneousSpeedValidatorTests(unittest.TestCase):

    #------------------------------------------
    def test_min_speed(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.y, enabled=True)
        validator.min_speed = 1

        validator.mouse_at(0, 0, 0)
        validator.mouse_at(0, 2, 1)
        validator.mouse_at(0, 3, 2)
        try:
            validator.mouse_at(0, 3.9, 3)
            self.fail()
        except ValidationFailed as e:
            self.assertEqual(InstantaneousSpeedValidator.err_too_slow, e.err_code)

    #------------------------------------------
    def test_max_speed(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.y, enabled=True)
        validator.max_speed = 1

        validator.mouse_at(0, 0, 0)
        validator.mouse_at(0, 0.5, 1)
        validator.mouse_at(0, 1.5, 2)
        try:
            validator.mouse_at(0, 2.6, 3)
            self.fail()
        except ValidationFailed as e:
            self.assertEqual(InstantaneousSpeedValidator.err_too_fast, e.err_code)

    #------------------------------------------
    def test_grace(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.y, enabled=True)
        validator.min_speed = 1
        validator.grace_period = 2

        validator.mouse_at(0, 0, 0)
        validator.mouse_at(0, 1, 2)
        self.assertRaises(ValidationFailed, lambda:validator.mouse_at(0, 2, 4))

    #------------------------------------------
    def test_disabled(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.y, enabled=False)
        validator.min_speed = 1

        validator.mouse_at(0, 0, 0)
        validator.enabled = True
        validator.mouse_at(0, 1, 2)

        self.assertRaises(ValidationFailed, lambda:validator.mouse_at(0, 2, 4))

    #------------------------------------------
    def test_reset(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.y, enabled=True)
        validator.min_speed = 1

        validator.mouse_at(0, 0, 0)
        validator.reset()
        validator.mouse_at(0, 1, 2)
        self.assertRaises(ValidationFailed, lambda:validator.mouse_at(0, 2, 4))

    #------------------------------------------
    def test_interval(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.y, enabled=True)
        validator.min_speed = 1
        validator.calc_speed_interval = 3
        validator.mouse_at(0, 0, 0)
        validator.mouse_at(0, 1, 2)
        self.assertRaises(ValidationFailed, lambda:validator.mouse_at(0, 2, 4))

    #------------------------------------------
    def test_speed_y(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.y, enabled=True, min_speed=1)
        validator.mouse_at(0, 0, 0)
        validator.mouse_at(0, 1, 1)
        self.assertRaises(ValidationFailed, lambda:validator.mouse_at(1, 1, 2))

    #------------------------------------------
    def test_speed_x(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.x, enabled=True, min_speed=1)
        validator.mouse_at(0, 0, 0)
        validator.mouse_at(1, 0, 1)
        self.assertRaises(ValidationFailed, lambda:validator.mouse_at(1, 1, 2))

    #------------------------------------------
    def test_speed_xy(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.xy, enabled=True, min_speed=5)
        validator.mouse_at(0, 0, 0)
        validator.mouse_at(3, 4, 1)

        validator.reset()
        validator.mouse_at(0, 0, 0)
        self.assertRaises(ValidationFailed, lambda:validator.mouse_at(3, 3.99, 1))

        validator.reset()
        validator.mouse_at(0, 0, 0)
        self.assertRaises(ValidationFailed, lambda:validator.mouse_at(2.99, 4, 1))



if __name__ == '__main__':
    unittest.main()
