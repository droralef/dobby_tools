"""

 traj tracker - a set of tools for psychological experiments under expyriment

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

"""


class InvalidStateError(StandardError):
    """ A method was called when the object is an inappropriate state """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class BadFormatError(StandardError):
    """ Data was provided in an invalid format (e.g., in a file) """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass



import expyriment as xpy


class _TTrkObject(object):

    def __init__(self):
        self.log_level = self.log_none


    #-- Log levels (each level will also print the higher log levels)
    log_trace = 1
    log_debug = 2
    log_info = 3
    log_warn = 4
    log_error = 5
    log_none = 9999

    @property
    def log_level(self):
        """Getter for logging level."""
        return self._log_level

    @log_level.setter
    def log_level(self, level):
        """
        Set the log level of this object
        :param level: Use the constants _TTrkObject.log_xxxxx
        """
        self._log_level = level


    #--------------------------------------------
    #-- Some default logging functions

    def _should_log(self, message_level):
        return message_level >= self._log_level


    #-------------------------------------------------
    def _log_setter(self, attr_name, value=None):

        if self._log_level > self.log_trace:
            return

        if value is None:
            value = str(self.__getattribute__(attr_name))

        if len(value) > 100:
            value = value[:100]

        self._log_write("set_obj_attr,{0}.{1},{2}".format(type(self).__name__, attr_name, value))


    #-------------------------------------------------
    def _log_write(self, msg):
        xpy._active_exp._event_file_log(msg, 1)


import trajtracker._utils as _utils

import trajtracker.misc as misc
import trajtracker.stimuli as stimuli
import trajtracker.movement as movement
import trajtracker.validators as validators
