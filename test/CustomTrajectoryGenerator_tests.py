import unittest

import trajtracker as ttrk
from trajtracker.movement import CustomTrajectoryGenerator


class CustomTrajectoryGeneratorTests(unittest.TestCase):

    #==========================================================================
    # Configure
    #==========================================================================

    #----------------------------------------------------------
    def test_create_empty(self):
        CustomTrajectoryGenerator()


    #----------------------------------------------------------
    def test_set_cyclic(self):
        gen = CustomTrajectoryGenerator()
        gen.cyclic = True

        self.assertRaises(TypeError, lambda: CustomTrajectoryGenerator(cyclic=1))
        self.assertRaises(TypeError, lambda: CustomTrajectoryGenerator(cyclic=None))


    #----------------------------------------------------------
    def test_set_interpolate(self):
        gen = CustomTrajectoryGenerator()
        gen.interpolate = True

        self.assertRaises(TypeError, lambda: CustomTrajectoryGenerator(interpolate=1))
        self.assertRaises(TypeError, lambda: CustomTrajectoryGenerator(interpolate=None))

    #----------------------------------------------------------
    def test_set_good_trajectory(self):
        gen = CustomTrajectoryGenerator()
        gen.set_trajectory(1, [(1, 0, 0, True)])
        gen.set_trajectory(2, [(0, 0, 0), (0.5, 0, 0)])

    #----------------------------------------------------------
    def test_set_active_traj(self):
        gen = CustomTrajectoryGenerator()
        gen.set_trajectory(1, [(1, 0, 0, True)])
        gen.set_trajectory(2, [(0, 0, 0), (1, 0, 0)])
        gen.active_traj_id = 1
        self.assertEqual(1, gen.active_traj_id)
        gen.active_traj_id = None

        try:
            gen.active_traj_id = 3
            self.fail()
        except ValueError:
            pass


    #----------------------------------------------------------
    def test_set_empty_traj(self):
        gen = CustomTrajectoryGenerator()
        self.assertRaises(TypeError, lambda: gen.set_trajectory(1, []))

    #----------------------------------------------------------
    def test_set_traj_invalid_time_point(self):
        gen = CustomTrajectoryGenerator()
        self.assertRaises(TypeError, lambda: gen.set_trajectory(1, [""]))
        self.assertRaises(TypeError, lambda: gen.set_trajectory(1, [(1, 2)]))
        self.assertRaises(TypeError, lambda: gen.set_trajectory(1, [(1, 2, 3, 4, 5)]))
        self.assertRaises(TypeError, lambda: gen.set_trajectory(1, [(None, 0, 0)]))
        self.assertRaises(TypeError, lambda: gen.set_trajectory(1, [("", 0, 0)]))
        self.assertRaises(TypeError, lambda: gen.set_trajectory(1, [(0, 0.1, 0)]))
        self.assertRaises(TypeError, lambda: gen.set_trajectory(1, [(0, None, 0)]))
        self.assertRaises(TypeError, lambda: gen.set_trajectory(1, [(0, 0, 0.1)]))
        self.assertRaises(TypeError, lambda: gen.set_trajectory(1, [(0, 0, None)]))
        self.assertRaises(TypeError, lambda: gen.set_trajectory(1, [(0, 0, 0, None)]))
        self.assertRaises(TypeError, lambda: gen.set_trajectory(1, [(0, 0, 0, 1)]))


    #----------------------------------------------------------
    def test_set_unordered_time_points(self):
        gen = CustomTrajectoryGenerator()
        self.assertRaises(ValueError, lambda: gen.set_trajectory(1, [(1, 0, 0), (1, 0, 0)]))
        self.assertRaises(ValueError, lambda: gen.set_trajectory(1, [(1, 0, 0), (0.5, 0, 0)]))


    #==========================================================================
    # Get trajectory data
    #==========================================================================

    #----------------------------------------------------------
    def test_get_traj_data_no_interpolate(self):

        gen = CustomTrajectoryGenerator(interpolate=False)
        gen.set_trajectory(1, [(0, 0, 1, True), (1, 1, 2, False), (2, 2, 3, True), (3, 3, 4, False)])

        pt = gen.get_traj_point(2)
        self.assertEqual(2, pt[0])
        self.assertEqual(3, pt[1])
        self.assertEqual(True, pt[2])

        pt = gen.get_traj_point(2.3)
        self.assertEqual(2, pt[0])
        self.assertEqual(3, pt[1])
        self.assertEqual(True, pt[2])

        pt = gen.get_traj_point(2.6)
        self.assertEqual(2, pt[0])
        self.assertEqual(3, pt[1])
        self.assertEqual(True, pt[2])


    #----------------------------------------------------------
    def test_get_traj_data_interpolate(self):

        gen = CustomTrajectoryGenerator(interpolate=True)
        gen.set_trajectory(1, [(0, 0, 1, True), (1, 10, 20, False), (2, 20, 30, True), (3, 30, 40, False)])

        pt = gen.get_traj_point(2)
        self.assertEqual(20, pt[0])
        self.assertEqual(30, pt[1])
        self.assertEqual(True, pt[2])

        pt = gen.get_traj_point(2.33)
        self.assertEqual(23, pt[0])
        self.assertEqual(33, pt[1])
        self.assertEqual(True, pt[2])

        pt = gen.get_traj_point(2.66)
        self.assertEqual(27, pt[0])
        self.assertEqual(37, pt[1])
        self.assertEqual(False, pt[2])



if __name__ == '__main__':
    unittest.main()
