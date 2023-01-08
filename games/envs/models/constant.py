from enum import Enum
from collections import namedtuple

Coord = namedtuple("Coordinate", ['x', 'y'])


class Direction(Enum):
    NONE = 0
    TOP = 1
    LEFT = 2
    BOTTOM = 3
    RIGHT = 4


class ProbType(Enum):
    EMPTY = 0
    SOLID = 1
    PLAYER = 2
    KEY = 3
    DOOR = 4
    BAT = 5
    SCORPION = 6
    SPIDER = 7


MOVE = {
    Direction.NONE: (0, 0),
    Direction.TOP: (-1, 0),
    Direction.LEFT: (0, -1),
    Direction.BOTTOM: (1, 0),
    Direction.RIGHT: (0, 1),
}
