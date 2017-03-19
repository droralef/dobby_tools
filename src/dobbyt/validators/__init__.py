"""

Dobby tools - validators package

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

"""

import enum


ValidationAxis = enum.Enum('ValidationAxis', 'x y xy')
SpeedError = enum.Enum('SpeedError', 'OK TooSlow TooFast')


from _ValidationFailed import ValidationFailed

from _GlobalSpeedValidator import GlobalSpeedValidator
from _InstantaneousSpeedValidator import InstantaneousSpeedValidator
from _LocationsValidator import LocationsValidator
from _MovementAngleValidator import MovementAngleValidator
from _MoveByGradientValidator import MoveByGradientValidator
