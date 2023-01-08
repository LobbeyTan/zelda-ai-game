import numpy as np
from games.envs.models.movable import Movable
from games.envs.models.constant import *


class Spider(Movable):

    def __init__(self, map: np.ndarray, coord: Coord) -> None:
        directions = [Direction.TOP, Direction.BOTTOM]
        prob_type = ProbType.SPIDER
        super().__init__(map, coord, directions, prob_type)

