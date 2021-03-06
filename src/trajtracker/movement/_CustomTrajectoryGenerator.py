"""

Custom trajectory generator

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division
import numbers
import numpy as np
import csv

import trajtracker
import trajtracker._utils as _u


class CustomTrajectoryGenerator(trajtracker._TTrkObject):
    """
    Create a movement trajectory for a stimulus, according to explicit definition.

    The definition can be loaded from a CSV file or specified programmatically.

    This class can hold several different trajectories. Each has its own ID. Before the trial
    starts, set the ID of the trajectory to play.

    Use this class in conjunction with :class:`~trajtracker.movement.StimulusAnimator`

    After loading trajectories, call :func:`~trajtracker.movement.CustomTrajectoryGenerator.validate`
    """

    _all_ok = "OK"


    def __init__(self, cyclic=False, interpolate=True):
        """
        Constructor

        :param cyclic: See :attr:`~trajtracker.movement.CustomTrajectoryGenerator.cyclic`
        :param interpolate:  See :attr:`~trajtracker.movement.CustomTrajectoryGenerator.interpolate`
        """

        super(CustomTrajectoryGenerator, self).__init__()

        self.clear_all_trajectories()
        self._traj_id = None

        self.interpolate = interpolate
        self.cyclic = cyclic
        self.active_traj_id = None
        self._validation_err = None


    #=================================================================
    #     Generate trajectory
    #=================================================================


    #---------------------------------------------------------------
    def get_traj_point(self, time):
        """
        Generate the trajectory - get one time point data

        :param time: in seconds
        :return: (x, y, visible)
        """

        self.validate()

        _u.validate_func_arg_type(self, "get_traj_point", "time", time, numbers.Number)
        _u.validate_func_arg_not_negative(self, "get_traj_point", "time", time)

        if self._active_traj_id is None:
            if len(self._trajectories):
                self.active_traj_id = self._trajectories.keys()[0]
            else:
                raise trajtracker.InvalidStateError("{:}.get_traj_point() cannot be called before active_traj_id was set".format(type(self).__name__))

        traj_inf = self._trajectories[self._active_traj_id]

        if time < traj_inf['times'][0]:
            raise ValueError("trajtracker error in {:}.get_traj_point(time={:}): the active trajectory ({:}) starts from time={:}".format(
                type(self).__name__, time, self._active_traj_id, traj_inf['times'][0]))

        #-- Time can't exceed the trajectory duration
        if time > traj_inf['duration']:
            time = time % traj_inf['duration'] if self._cyclic else traj_inf['duration']

        traj_times = traj_inf['times']
        traj_xy = traj_inf['coords']
        traj_visible = traj_inf['visible']


        ind_before_time = np.where(traj_times <= time)[0][-1]
        time_before = traj_times[ind_before_time]

        coord_before = traj_xy[ind_before_time]
        visible_before = traj_visible[ind_before_time]

        if time_before == time:
            ind_after_time = ind_before_time
            time_after = time_before
        else:
            ind_after_time = min(ind_before_time+1, len(traj_times)-1)
            time_after = traj_times[ind_after_time]

        if self._interpolate and time_before != time_after:

            #-- Coordinates: linear interpolation between the two relevant time points
            coord_after = traj_xy[ind_after_time]
            weight_of_after_ind = (time - time_before) / (time_after - time_before)
            weight_of_before_ind = 1 - weight_of_after_ind
            x = int( np.round(coord_before[0] * weight_of_before_ind + coord_after[0] * weight_of_after_ind) )
            y = int( np.round(coord_before[1] * weight_of_before_ind + coord_after[1] * weight_of_after_ind) )

            #-- Visibility: use the value from the closest available time point
            visible_after = traj_visible[ind_after_time]
            visible = visible_before if weight_of_before_ind > weight_of_after_ind else visible_after

            return x, y, visible

        else:
            #-- Return the value of the last time point before "time"
            return coord_before + (visible_before, )


    #---------------------------------------------------------------
    @property
    def active_traj_id(self):
        """
        The ID of the active trajectory
        """
        return self._active_traj_id

    @active_traj_id.setter
    def active_traj_id(self, value):
        if value is not None and value not in self._trajectories:
            raise ValueError("trajtracker error: invalid {:}.curr_traj_id ({:}) - no trajectory with this ID".format(type(self).__name__, value))
        self._active_traj_id = value


    #=================================================================
    #     Configure
    #=================================================================

    #---------------------------------------------------------------
    def clear_all_trajectories(self):
        """
        Forget all previously-defined trajectories
        """
        self._trajectories = {}
        self._validation_err = None


    #---------------------------------------------------------------
    def set_trajectory(self, traj_id, traj_data):
        """
        Add a single trajectory (or replace an existing one)

        :param traj_id: A logical ID for this trajectory.
        :param traj_data: The trajectory data - a list/tuple of per-timepoint data.
                Per time point, specify a list/tuple of with 3 or 4 elements: time (> 0),
                x coordinate (int), y coordinate (int), and optional "visible" (bool)
        """

        _u.validate_func_arg_anylist(self, "set_trajectory", "traj_data", traj_data, min_length=1)
        if traj_id is None:
            raise TypeError("trajtracker error: {:}.set_trajectory(traj_id=None) is invalid".format(type(self).__name__))

        coords = []
        times = []
        visible = []
        prev_time = -1

        for i in range(len(traj_data)):

            time_point = traj_data[i]

            _u.validate_func_arg_anylist(self, "set_trajectory", "traj_data[%d]" % i, time_point, min_length=3, max_length=4)
            _u.validate_func_arg_type(self, "set_trajectory", "traj_data[%d][0]" % i, time_point[0], numbers.Number)
            _u.validate_func_arg_not_negative(self, "set_trajectory", "traj_data[%d][0]" % i, time_point[0])
            _u.validate_func_arg_type(self, "set_trajectory", "traj_data[%d][1]" % i, time_point[1], int)
            _u.validate_func_arg_type(self, "set_trajectory", "traj_data[%d][2]" % i, time_point[2], int)

            time = time_point[0]
            if time <= prev_time:
                raise ValueError(("trajtracker error: {:}.set_trajectory() called with invalid value for trajectory '{:}' " +
                                 "- timepoint {:} appeared after {:}").format(type(self).__name__, traj_id, time, prev_time))

            prev_time = time

            times.append(time)
            coords.append((time_point[1], time_point[2]))

            if len(time_point) == 4:
                _u.validate_func_arg_type(self, "set_trajectory", "traj_data[%d][3]" % i, time_point[3], bool)
                visible.append(time_point[3])
            else:
                visible.append(True)

        self._trajectories[traj_id] = {
            'times': np.array(times),
            'coords': coords,
            'visible': visible,
            'duration': times[-1]
        }

        self._validation_err = None


    #---------------------------------------------------------------
    def load_from_csv(self, filename, id_type=str):
        """
        Load trajectories from a CSV file.

        The file should have the following columns:

        - x, y: the coordinates
        - time: a time point of these coordinates
        - visible: whether the stimulus should be visible in this time point
        - traj_id: use this column to specify several trajectories in a single file. If this column
          is missing, the class assumes that there is only one trajectory in the file, and its ID will be 1.

        The file should be sorter properly: all lines of a single trajectory should be grouped together, and
        times should appear in ascending order.

        :param filename: Name of the file (full path)
        :param id_type: Convert the traj_id column in the file from str to this type
        """

        _u.validate_func_arg_type(self, "load_from_csv", "filename", filename, str)

        fp, reader = self._open_and_get_reader(filename)
        has_traj_id_col = 'traj_id' in reader.fieldnames
        has_visible_col = 'visible' in reader.fieldnames

        if len(self._trajectories) > 0 and not has_traj_id_col:
            raise trajtracker.BadFormatError(("Invalid file format in {:}.load_from_csv('{:}'): " +
                                             "there is no traj_id column in the file").format(type(self).__name__, filename))

        loaded_traj_ids = set()

        try:
            #-- Validate file format
            for col_name in ['x', 'y', 'time']:
                if col_name not in reader.fieldnames:
                    raise trajtracker.BadFormatError(
                        "Invalid file format in {:}.load_from_csv('{:}'): there is no '{:}' column".format(
                            type(self).__name__, filename, col_name))


            prev_traj_id = None
            traj_data = []

            for row in reader:

                traj_id = id_type(row['traj_id']) if has_traj_id_col else 1
                if traj_id in loaded_traj_ids:
                    raise trajtracker.BadFormatError(
                        "Invalid file format in {:}.load_from_csv('{:}'): the lines of trajectory '{:}' are not consecutive".format(
                            type(self).__name__, filename, traj_id))


                if prev_traj_id is None:
                    # First trajectory in the file
                    prev_traj_id = traj_id

                elif prev_traj_id is not None and prev_traj_id != traj_id:
                    #-- A new trajectory is starting; save the trajectory that has just ended
                    self.set_trajectory(prev_traj_id, traj_data)
                    loaded_traj_ids.add(prev_traj_id)
                    traj_data = []
                    prev_traj_id = traj_id

                #-- Save current line as a time point

                time = float(row['time'])
                x = int(row['x'])
                y = int(row['y'])

                if has_visible_col:
                    visible = not (row['visible'] == '0' or row['visible'].lower().startswith('f'))
                    timepoint = (time, x, y, visible)
                else:
                    timepoint = (time, x, y)

                traj_data.append(timepoint)


            if len(traj_data) > 0:
                self.set_trajectory(prev_traj_id, traj_data)


        finally:
            fp.close()



    def _open_and_get_reader(self, filename):
        fp = open(filename, 'r')
        try:
            return fp, csv.DictReader(fp)
        except object as e:
            fp.close()
            raise


    #---------------------------------------------------------------
    def validate(self):
        """
        Validate that the configuration is correct. Raise an exception if not.
        """

        if self._validation_err == self._all_ok:
            return
        elif self._validation_err is not None:
            raise self._validation_err

        if self._cyclic:
            for traj_id in self._trajectories:
                t0 = self._trajectories[traj_id]['times'][0]
                if t0 > 0:
                    self._validation_err = ValueError(
                        ("trajtracker error: invalid trajectory configuration in {:}: when cyclic=True " +
                        "all trajectories must start from time=0, but trajectory '{:}' starts from " +
                        "time={:}").format(type(self).__name__, traj_id, t0))
                    raise self._validation_err

        self._validation_err = self._all_ok


    #---------------------------------------------------------------
    @property
    def interpolate(self):
        """
        This determines what happens when get_traj_point() is called with time that was not specifically defined in
        the trajectory:

        - True: interpolate linearly the two nearest time points
        - False: Use data from the last timepoint <= time
        """
        return self._interpolate

    @interpolate.setter
    def interpolate(self, value):
        _u.validate_attr_type(self, "interpolate", value, bool)
        self._interpolate = value


    #---------------------------------------------------------------
    @property
    def cyclic(self):
        """
        Whether the trajectory is cyclic or not (bool). In a cyclic trajectory, when the time exceeds the
        trajectory duration, we return to the starting point.
        """
        return self._cyclic

    @cyclic.setter
    def cyclic(self, value):
        _u.validate_attr_type(self, "interpolate", value, bool)
        self._cyclic = value

        self._validation_err = None

