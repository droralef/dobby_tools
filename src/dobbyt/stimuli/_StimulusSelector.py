"""

Stimulus selector: show one of several stimuli

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import dobbyt
import dobbyt._utils as _u


class StimulusSelector(dobbyt._DobbyObject):
    """
    Keep several expyriment stimuli, only one of which is selected.
    Allow changing the selected stimulus, updating its position, and presenting it
    """

    def __init__(self, stimuli=()):

        super(StimulusSelector, self).__init__()

        self._selected_key = None
        self._stimuli = {}

        for key, stim in stimuli:
            self.add_stimulus(key, stim)


    #--------------------------------------------------
    def add_stimulus(self, key, stim):
        self._stimuli[key] = stim


    #--------------------------------------------------
    def select(self, key):
        if key is None or key in self._stimuli:
            self._selected_key = key
        else:
            raise ValueError("dobbyt error: {:}.select(key={:}) - this stimulus was not defined".format(type(self).__name__, key))


    #--------------------------------------------------
    @property
    def selected_stimulus(self):
        if self._selected_key is None:
            return None
        else:
            return self._stimuli[self._selected_key]

    @property
    def selected_key(self):
        return self._selected_key

    #--------------------------------------------------
    def present(self, clear, update):
        s = self.selected_stimulus
        s.present(clear=clear, update=update)


    #--------------------------------------------------
    @property
    def position(self):
        s = self.selected_stimulus
        return None if s is None else s.position

    @position.setter
    def position(self, value):
        s = self.selected_stimulus
        if s is not None:
            s.position = value
