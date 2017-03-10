"""

dobbyt (Dobby Tools package) - a set of tools for psychological experiments under expyriment

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

"""


class _Dobby_Object(object):

    def __init__(self):
        self.set_logging(False)


    def set_logging(self, onoff):
        """Set logging of this object on or off

        Parameters
        ----------
        onoff : set logging on (True) or off (False)

        Notes
        -----
        See also expyriment.design.experiment.set_log_level fur further information about
        event logging.
    """
        self._logging = onoff


    def logging(self):
        """Getter for logging on/off flag."""
        return self._logging



class InvalidStateError(StandardError):
    """ A method was called when the object is an inappropriate state """
    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    @staticmethod # known case of __new__
    def __new__(S, *more): # real signature unknown; restored from __doc__
        """ T.__new__(S, ...) -> a new object with type S, a subtype of T """
        pass


import dobbyt.stimuli as controls
