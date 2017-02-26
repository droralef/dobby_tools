import unittest


from dobbyt.movement import InstantaneousSpeedValidator

rc_ok = InstantaneousSpeedValidator.ErrType.OK
rc_slow = InstantaneousSpeedValidator.ErrType.TooSlow
rc_fast = InstantaneousSpeedValidator.ErrType.TooFast


class InstantaneousSpeedValidatorTests(unittest.TestCase):

    #------------------------------------------
    def test_min_speed(self):
        validator = InstantaneousSpeedValidator(1, axis=InstantaneousSpeedValidator.Axis.y, enabled=True)
        validator.min_speed = 1

        self.assertEqual(rc_ok, validator.mouse_at(0, 0, 0))
        self.assertEqual(rc_ok, validator.mouse_at(0, 2, 1))
        self.assertEqual(rc_ok, validator.mouse_at(0, 3, 2))
        self.assertEqual(rc_slow, validator.mouse_at(0, 3.9, 3))

    #------------------------------------------
    def test_max_speed(self):
        validator = InstantaneousSpeedValidator(1, axis=InstantaneousSpeedValidator.Axis.y, enabled=True)
        validator.max_speed = 1

        self.assertEqual(rc_ok, validator.mouse_at(0, 0, 0))
        self.assertEqual(rc_ok, validator.mouse_at(0, 0.5, 1))
        self.assertEqual(rc_ok, validator.mouse_at(0, 1.5, 2))
        self.assertEqual(rc_fast, validator.mouse_at(0, 2.6, 3))

    #------------------------------------------
    def test_grace(self):
        validator = InstantaneousSpeedValidator(1, axis=InstantaneousSpeedValidator.Axis.y, enabled=True)
        validator.min_speed = 1
        validator.grace_period = 2

        self.assertEqual(rc_ok, validator.mouse_at(0, 0, 0))
        self.assertEqual(rc_ok, validator.mouse_at(0, 1, 2))
        self.assertEqual(rc_slow, validator.mouse_at(0, 2, 4))

    #------------------------------------------
    def test_disabled(self):
        validator = InstantaneousSpeedValidator(1, axis=InstantaneousSpeedValidator.Axis.y, enabled=False)
        validator.min_speed = 1

        self.assertEqual(rc_ok, validator.mouse_at(0, 0, 0))
        validator.enabled = True
        self.assertEqual(rc_ok, validator.mouse_at(0, 1, 2))
        self.assertEqual(rc_slow, validator.mouse_at(0, 2, 4))

    #------------------------------------------
    def test_reset(self):
        validator = InstantaneousSpeedValidator(1, axis=InstantaneousSpeedValidator.Axis.y, enabled=True)
        validator.min_speed = 1

        self.assertEqual(rc_ok, validator.mouse_at(0, 0, 0))
        validator.reset()
        self.assertEqual(rc_ok, validator.mouse_at(0, 1, 2))
        self.assertEqual(rc_slow, validator.mouse_at(0, 2, 4))

    #------------------------------------------
    def test_interval(self):
        validator = InstantaneousSpeedValidator(1, axis=InstantaneousSpeedValidator.Axis.y, enabled=True)
        validator.min_speed = 1
        validator.calc_speed_interval = 3
        self.assertEqual(rc_ok, validator.mouse_at(0, 0, 0))
        self.assertEqual(rc_ok, validator.mouse_at(0, 1, 2))
        self.assertEqual(rc_slow, validator.mouse_at(0, 2, 4))

    #------------------------------------------
    def test_speed_y(self):
        validator = InstantaneousSpeedValidator(1, axis=InstantaneousSpeedValidator.Axis.y, enabled=True, min_speed=1)
        self.assertEqual(rc_ok, validator.mouse_at(0, 0, 0))
        self.assertEqual(rc_ok, validator.mouse_at(0, 1, 1))
        self.assertEqual(rc_slow, validator.mouse_at(1, 1, 2))

    #------------------------------------------
    def test_speed_x(self):
        validator = InstantaneousSpeedValidator(1, axis=InstantaneousSpeedValidator.Axis.x, enabled=True, min_speed=1)
        self.assertEqual(rc_ok, validator.mouse_at(0, 0, 0))
        self.assertEqual(rc_ok, validator.mouse_at(1, 0, 1))
        self.assertEqual(rc_slow, validator.mouse_at(1, 1, 2))

    #------------------------------------------
    def test_speed_xy(self):
        validator = InstantaneousSpeedValidator(1, axis=InstantaneousSpeedValidator.Axis.xy, enabled=True, min_speed=5)
        self.assertEqual(rc_ok, validator.mouse_at(0, 0, 0))
        self.assertEqual(rc_ok, validator.mouse_at(3, 4, 1))

        validator.reset()
        self.assertEqual(rc_ok, validator.mouse_at(0, 0, 0))
        self.assertEqual(rc_slow, validator.mouse_at(3, 3.99, 1))

        validator.reset()
        self.assertEqual(rc_ok, validator.mouse_at(0, 0, 0))
        self.assertEqual(rc_slow, validator.mouse_at(2.99, 4, 1))



if __name__ == '__main__':
    unittest.main()
