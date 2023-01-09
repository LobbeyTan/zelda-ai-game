import numpy as np
from scipy.signal import convolve2d
from games.envs.generators.map_generator import MapGenerator


class CellularAutomata(MapGenerator):

    def __init__(self, rand: np.random, width: int, height: int, p=0.55) -> None:
        super().__init__(rand, width, height, p)
        self.X = self.rand.choice([0, 1], size=(width, height), p=[1-p, p])

    def generateMap(self) -> np.ndarray:
        for _ in range(2):
            self.X = self.ca_step()

        return self.X

    def ca_step_conv(self, X) -> np.ndarray:
        """Evolve the maze by a single CA step."""

        K = np.ones((3, 3))
        n = convolve2d(X, K, mode='same', boundary='wrap') - X
        return (n == 3) | (X & ((n > 0) & (n < 6)))

    def ca_step(self, threshold=4) -> np.ndarray:
        """Evolve the maze by a single CA step."""

        width, height = self.X.shape

        tmp = self.X.copy()

        for x in range(width):
            for y in range(height):
                neighbour_wall = self.get_all_neighbour(x, y)

                tmp[x][y] = int(neighbour_wall > threshold)

        return tmp

    def get_all_neighbour(self, x, y):
        wall_count = 0

        for dx in range(x-1, x+2):
            for dy in range(y-1, y+2):

                if self.is_within_bound(self.X, dx, dy):
                    if (not (dx == x and dy == y)):
                        wall_count += self.X[dx][dy]
                else:
                    wall_count += 1

        return wall_count
