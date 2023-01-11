
import numpy as np
from gym.utils import seeding
from games.envs.models.constant import *


class Movable:

    def __init__(self, map: np.ndarray, coord: Coord, directions: list[Direction], prob_type: ProbType, deterministic=True) -> None:
        self.seed()
        self.deterministic = deterministic
        self.map = map

        self.last_coord: Coord = None
        self.initial_coord: Coord = coord
        self.current_coord: Coord = coord

        self.possible_directions: list[Direction] = directions
        self.prob_type: ProbType = prob_type
        self.dir_index = 0 if self.deterministic else self._random.randint(0, len(self.possible_directions))
        self.direction: Direction = self.possible_directions[self.dir_index]

    def isValidMove(self) -> bool:
        dx, dy = MOVE[self.direction]

        x, y = self.current_coord.x + dx, self.current_coord.y + dy

        if self.isWithinBound(x, y):
            next_tile = self.map[x][y]
            return next_tile in [0, 2]

        return False

    def seed(self, seed=None):
        self._random, seed = seeding.np_random(seed)
        return seed

    def step(self):
        hasValidMove = False

        for _ in range(len(self.possible_directions)):
            if self.isValidMove():
                hasValidMove = True
                break
            self.changeDirection()

        if not hasValidMove:
            self.direction = Direction.NONE

        dx, dy = MOVE[self.direction]

        self.last_coord = self.current_coord
        self.current_coord = Coord(self.current_coord.x + dx, self.current_coord.y + dy)

        self.map[self.last_coord.x][self.last_coord.y] = 0
        self.map[self.current_coord.x][self.current_coord.y] = self.prob_type.value

    def changeDirection(self):
        self.dir_index += 1
        self.direction = self.possible_directions[self.dir_index % len(self.possible_directions)]

    def isWithinBound(self, dx, dy):
        width, height = self.map.shape
        return dx >= 0 and dy >= 0 and dx < width and dy < height

    def reset(self):
        self.current_coord = self.initial_coord
        self.last_coord = None
        
        self.dir_index = 0 if self.deterministic else self._random.randint(0, len(self.possible_directions))
        self.direction: Direction = self.possible_directions[self.dir_index]