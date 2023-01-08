import numpy as np
from games.envs.models.movable import Movable
from games.envs.models.constant import *


class Bat(Movable):

    def __init__(self, map: np.ndarray, coord: Coord) -> None:
        directions = [Direction.TOP, Direction.LEFT, Direction.BOTTOM, Direction.RIGHT]
        prob_type = ProbType.BAT
        super().__init__(map, coord, directions, prob_type)
