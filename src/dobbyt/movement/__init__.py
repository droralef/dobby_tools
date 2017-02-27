"""

Dobby tools - movement package

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

"""

import enum

ValidationAxis = enum.Enum('ValidationAxis', 'x y xy')
SpeedError = enum.Enum('SpeedError', 'OK TooSlow TooFast')


#  Import the package classes
from _DirectionValidator import DirectionValidator
from _GlobalSpeedValidator import GlobalSpeedValidator
from _InstantaneousSpeedValidator import InstantaneousSpeedValidator
from _TrajectoryTracker import TrajectoryTracker
from _utils import get_angle
