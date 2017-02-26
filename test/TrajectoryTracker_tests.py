import unittest

from dobbyt.movement import TrajectoryTracker
from dobbyt_testing import DummyFileHandle


class TrajectoryTrackerForTesting(TrajectoryTracker):

    def _open_file(self, filename, mode):

        if mode == 'w':
            self._file_data = DummyFileHandle()

        return self._file_data



class TrajectoryTrackerTestCase(unittest.TestCase):

    #------------------------------------------------------------------
    def test_track(self):

        ttrk = TrajectoryTrackerForTesting(True)
        ttrk.init_output_file("stam", xy_precision=1, time_precision=1)

        ttrk.track(1, 1.5, 0.1)
        ttrk.track(2, 2.5, 0.2)
        ttrk.save_to_file(0)

        ttrk.reset(True)
        ttrk.track(12, 2.5, 0.2)
        ttrk.track(13, 3.5, 0.3)
        ttrk.save_to_file(1)

        self.assertEqual("trial,time,x,y\n0,0.1,1,1.5\n0,0.2,2,2.5\n1,0.2,12,2.5\n1,0.3,13,3.5\n", ttrk._file_data.data)

        xyt = ttrk.get_xyt()
        self.assertEqual(2, len(xyt))
        self.assertEqual((12,2.5,0.2), xyt[0])
        self.assertEqual((13,3.5,0.3), xyt[1])


    #------------------------------------------------------------------
    def test_track_active_inactive(self):

        ttrk = TrajectoryTrackerForTesting()
        ttrk.init_output_file("stam", xy_precision=1, time_precision=1)

        ttrk.track(1, 1.5, 0.1)
        ttrk.tracking_active = True
        ttrk.track(2, 2.5, 0.2)
        ttrk.track(3, 3.5, 0.3)
        ttrk.tracking_active = False
        ttrk.track(4, 4.5, 0.4)
        ttrk.save_to_file(0)

        self.assertEqual("trial,time,x,y\n0,0.2,2,2.5\n0,0.3,3,3.5\n", ttrk._file_data.data)

    #------------------------------------------------------------------
    def test_prec(self):

        ttrk = TrajectoryTrackerForTesting(True)
        ttrk.init_output_file("stam", xy_precision=2, time_precision=3)
        ttrk.track(0.2, 0.3, 0.1)
        ttrk.save_to_file(0)

        self.assertEqual("trial,time,x,y\n0,0.100,0.20,0.30\n", ttrk._file_data.data)

    #------------------------------------------------------------------
    def test_non_numeric_time(self):
        ttrk = TrajectoryTrackerForTesting()
        try:
            ttrk.track(0.2, 0.3, "")
            self.fail("Succeeded tracking a non-numeric time")
        except(Exception):
            pass


    #------------------------------------------------------------------
    def test_negative_time(self):
        ttrk = TrajectoryTrackerForTesting()
        try:
            ttrk.track(0.2, 0.3, -1)
            self.fail("Succeeded tracking a negative time")
        except(Exception):
            pass


    #------------------------------------------------------------------
    def test_non_numeric_x(self):
        ttrk = TrajectoryTrackerForTesting()
        try:
            ttrk.track("", 0.3, 0)
            self.fail("Succeeded tracking a non-numeric x coord")
        except(Exception):
            pass


    #------------------------------------------------------------------
    def test_non_numeric_y(self):
        ttrk = TrajectoryTrackerForTesting()
        try:
            ttrk.track(0.2, "", 0.3)
            self.fail("Succeeded tracking a non-numeric y coord")
        except(Exception):
            pass




if __name__ == '__main__':
    unittest.main()
