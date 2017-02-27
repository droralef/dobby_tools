import unittest


from dobbyt.movement import InstantaneousSpeedValidator, ValidationAxis, SpeedError



class InstantaneousSpeedValidatorTests(unittest.TestCase):

    #------------------------------------------
    def test_min_speed(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.y, active=True)
        validator.min_speed = 1

        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 0, 0))
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 2, 1))
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 3, 2))
        self.assertEqual(SpeedError.TooSlow, validator.mouse_at(0, 3.9, 3))

    #------------------------------------------
    def test_max_speed(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.y, active=True)
        validator.max_speed = 1

        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 0, 0))
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 0.5, 1))
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 1.5, 2))
        self.assertEqual(SpeedError.TooFast, validator.mouse_at(0, 2.6, 3))

    #------------------------------------------
    def test_grace(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.y, active=True)
        validator.min_speed = 1
        validator.grace_period = 2

        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 0, 0))
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 1, 2))
        self.assertEqual(SpeedError.TooSlow, validator.mouse_at(0, 2, 4))

    #------------------------------------------
    def test_disabled(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.y, active=False)
        validator.min_speed = 1

        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 0, 0))
        validator.active = True
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 1, 2))
        self.assertEqual(SpeedError.TooSlow, validator.mouse_at(0, 2, 4))

    #------------------------------------------
    def test_reset(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.y, active=True)
        validator.min_speed = 1

        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 0, 0))
        validator.reset()
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 1, 2))
        self.assertEqual(SpeedError.TooSlow, validator.mouse_at(0, 2, 4))

    #------------------------------------------
    def test_interval(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.y, active=True)
        validator.min_speed = 1
        validator.calc_speed_interval = 3
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 0, 0))
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 1, 2))
        self.assertEqual(SpeedError.TooSlow, validator.mouse_at(0, 2, 4))

    #------------------------------------------
    def test_speed_y(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.y, active=True, min_speed=1)
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 0, 0))
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 1, 1))
        self.assertEqual(SpeedError.TooSlow, validator.mouse_at(1, 1, 2))

    #------------------------------------------
    def test_speed_x(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.x, active=True, min_speed=1)
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 0, 0))
        self.assertEqual(SpeedError.OK, validator.mouse_at(1, 0, 1))
        self.assertEqual(SpeedError.TooSlow, validator.mouse_at(1, 1, 2))

    #------------------------------------------
    def test_speed_xy(self):
        validator = InstantaneousSpeedValidator(1, axis=ValidationAxis.xy, active=True, min_speed=5)
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 0, 0))
        self.assertEqual(SpeedError.OK, validator.mouse_at(3, 4, 1))

        validator.reset()
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 0, 0))
        self.assertEqual(SpeedError.TooSlow, validator.mouse_at(3, 3.99, 1))

        validator.reset()
        self.assertEqual(SpeedError.OK, validator.mouse_at(0, 0, 0))
        self.assertEqual(SpeedError.TooSlow, validator.mouse_at(2.99, 4, 1))



if __name__ == '__main__':
    unittest.main()
