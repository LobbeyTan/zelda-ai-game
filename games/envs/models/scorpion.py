import numpy as np
from games.envs.models.movable import Movable
from games.envs.models.constant import *


class Scorpion(Movable):

    def __init__(self, map: np.ndarray, coord: Coord) -> None:
        directions = [Direction.LEFT, Direction.RIGHT]
        prob_type = ProbType.SCORPION
        super().__init__(map, coord, directions, prob_type)
