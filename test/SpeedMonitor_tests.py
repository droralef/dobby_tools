import unittest

import numpy as np

import trajtracker
from trajtracker.movement import SpeedMonitor


class SpeedMonitorTests(unittest.TestCase):

    #=====================================================================================
    #           Configure object
    #=====================================================================================

    #---------------------------------------------------------
    def test_set_units_per_mm(self):
        m = SpeedMonitor(2, 10)

        try:
            m.units_per_mm = ""
            self.fail()
        except TypeError:
            pass

        try:
            m.units_per_mm = None
            self.fail()
        except TypeError:
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
        m = SpeedMonitor(2, 10)

        m.calculation_interval = 0

        try:
            m.calculation_interval = ""
            self.fail()
        except TypeError:
            pass

        try:
            m.calculation_interval = None
            self.fail()
        except TypeError:
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
        m = SpeedMonitor(2, 10)
        m.update_xyt(1, 1, 1)
        m.update_xyt(1, 1, 2)
        self.assertRaises(trajtracker.InvalidStateError, lambda: m.update_xyt(1, 1, 1))

    #---------------------------------------------------------
    def test_time_moves_backwards_from_reset(self):
        m = SpeedMonitor(2, 10)
        m.reset(1)
        self.assertRaises(trajtracker.InvalidStateError, lambda: m.update_xyt(1, 1, 0.5))


    #=====================================================================================
    #           speed
    #=====================================================================================

    #---------------------------------------------------------
    def test_x_speed(self):
        m = SpeedMonitor(2, 0.5)
        m.update_xyt(0, 0, 1)
        m.update_xyt(10, 2, 2)
        self.assertEqual(5, m.xspeed)


    #---------------------------------------------------------
    def test_y_speed(self):
        m = SpeedMonitor(2, 0.5)
        m.update_xyt(0, 0, 1)
        m.update_xyt(10, 2, 2)
        self.assertEqual(1, m.yspeed)


    #---------------------------------------------------------
    def test_xy_speed(self):
        m = SpeedMonitor(2, 0.5)
        m.update_xyt(0, 0, 1)
        m.update_xyt(0, 2, 2)
        m.update_xyt(2, 2, 3)
        self.assertEqual(1, m.xyspeed)

        m.reset()
        m.update_xyt(0, 0, 1)
        m.update_xyt(1, 1, 2)
        m.update_xyt(2, 2, 3)
        self.assertEqual(np.sqrt(2)/2, m.xyspeed)


    #---------------------------------------------------------
    def test_speed_na_before_calc_interval(self):
        m = SpeedMonitor(2, 10)
        m.update_xyt(0, 0, 20)
        self.assertIsNone(m.xspeed)
        self.assertIsNone(m.yspeed)
        self.assertIsNone(m.xyspeed)

        m.update_xyt(10, 2, 29)
        self.assertIsNone(m.xspeed)
        self.assertIsNone(m.yspeed)
        self.assertIsNone(m.xyspeed)

        m.update_xyt(10, 2, 30)
        self.assertIsNotNone(m.xspeed)
        self.assertIsNotNone(m.yspeed)
        self.assertIsNotNone(m.xyspeed)




if __name__ == '__main__':
    unittest.main()
