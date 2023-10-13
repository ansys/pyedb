"""
This module contains EDB general methods and related methods.

"""

from __future__ import absolute_import  # noreorder
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PadGeometryTpe(Enum):  # pragma: no cover
    Circle = 1
    Square = 2
    Rectangle = 3
    Oval = 4
    Bullet = 5
    NSidedPolygon = 6
    Polygon = 7
    Round45 = 8
    Round90 = 9
    Square45 = 10
    Square90 = 11
    InvalidGeometry = 12


class DielectricExtentType(Enum):
    BoundingBox = 0
    Conforming = 1
    ConvexHull = 2
    Polygon = 3


class BoundaryType(Enum):
    InvalidBoundary = -1
    PortBoundary = 0
    PecBoundary = 1
    RlcBoundary = 2
    kCurrentSource = 3
    kVoltageSource = 4
    kNexximGround = 5
    kNexximPort = 6
    kDcTerminal = 7
    kVoltageProbe = 8


class TerminalType(Enum):
    InvalidTerminal = -1
    EdgeTerminal = 0
    PointTerminal = 1
    TerminalInstanceTerminal = 2
    PadstackInstanceTerminal = 3
    BundleTerminal = 4
    PinGroupTerminal = 5
