import unittest

import numpy as np

import dobbyt
from dobbyt.movement import InstMovementMonitor


class InstMovementMonitorTests(unittest.TestCase):

    #=====================================================================================
    #           Configure object
    #=====================================================================================

    #---------------------------------------------------------
    def test_set_units_per_mm(self):
        m = InstMovementMonitor(2, 10)

        try:
            m.units_per_mm = ""
            self.fail()
        except ValueError:
            pass

        try:
            m.units_per_mm = None
            self.fail()
        except ValueError:
            pass

        try:
            m.units_per_mm = 0
            self.fail()
        except ValueError:
            pass

        try:
            m.units_per_mm = -1
            self.fail()
        except ValueError:
            pass


    #---------------------------------------------------------
    def test_set_calc_interval(self):
        m = InstMovementMonitor(2, 10)

        try:
            m.calculation_interval = ""
            self.fail()
        except ValueError:
            pass

        try:
            m.calculation_interval = None
            self.fail()
        except ValueError:
            pass

        try:
            m.calculation_interval = 0
            self.fail()
        except ValueError:
            pass

        try:
            m.calculation_interval = -1
            self.fail()
        except ValueError:
            pass


    #=====================================================================================
    #           Calls
    #=====================================================================================

    #---------------------------------------------------------
    def test_time_moves_backwards(self):
        m = InstMovementMonitor(2, 10)
        m.mouse_at(1, 1, 1)
        m.mouse_at(1, 1, 2)
        self.assertRaises(dobbyt.InvalidStateError, lambda: m.mouse_at(1, 1, 1))

    #---------------------------------------------------------
    def test_time_moves_backwards_from_reset(self):
        m = InstMovementMonitor(2, 10)
        m.reset(1)
        self.assertRaises(dobbyt.InvalidStateError, lambda: m.mouse_at(1, 1, 0.5))


    #=====================================================================================
    #           speed
    #=====================================================================================

    #---------------------------------------------------------
    def test_x_speed(self):
        m = InstMovementMonitor(2, 0.5)
        m.mouse_at(0, 0, 1)
        m.mouse_at(10, 2, 2)
        self.assertEqual(5, m.xspeed)


    #---------------------------------------------------------
    def test_y_speed(self):
        m = InstMovementMonitor(2, 0.5)
        m.mouse_at(0, 0, 1)
        m.mouse_at(10, 2, 2)
        self.assertEqual(1, m.yspeed)


    #---------------------------------------------------------
    def test_xy_speed(self):
        m = InstMovementMonitor(2, 0.5)
        m.mouse_at(0, 0, 1)
        m.mouse_at(0, 2, 2)
        m.mouse_at(2, 2, 3)
        self.assertEqual(1, m.xyspeed)

        m.reset()
        m.mouse_at(0, 0, 1)
        m.mouse_at(1, 1, 2)
        m.mouse_at(2, 2, 3)
        self.assertEqual(np.sqrt(2)/2, m.xyspeed)


    #---------------------------------------------------------
    def test_speed_na_before_calc_interval(self):
        m = InstMovementMonitor(2, 10)
        m.mouse_at(0, 0, 20)
        self.assertIsNone(m.xspeed)
        self.assertIsNone(m.yspeed)
        self.assertIsNone(m.xyspeed)

        m.mouse_at(10, 2, 29)
        self.assertIsNone(m.xspeed)
        self.assertIsNone(m.yspeed)
        self.assertIsNone(m.xyspeed)

        m.mouse_at(10, 2, 30)
        self.assertIsNotNone(m.xspeed)
        self.assertIsNotNone(m.yspeed)
        self.assertIsNotNone(m.xyspeed)


    #=====================================================================================
    #           angle
    #=====================================================================================

    #---------------------------------------------------------
    def test_angle(self):
        m = InstMovementMonitor(2, 10)
        self.fail('write this test; also, use InstMovementMonitor for speed/angle validation')



if __name__ == '__main__':
    unittest.main()
