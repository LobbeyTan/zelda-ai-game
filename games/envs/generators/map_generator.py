import numpy as np
from collections import namedtuple


Coord = namedtuple("Coord", ["x", "y"])


class MapGenerator:

    def __init__(self, rand: np.random, width: int, height: int, p: float) -> None:
        self.map = None
        self.rand = rand
        self.width = width
        self.height = height
        self.p = p

    def generateMap(self) -> np.ndarray:
        raise NotImplementedError('map is not generated')

    def getMap(self) -> np.ndarray:
        self.map = self.generateMap()
        self.process()
        self.populateProp()

        return self.map

    def process(self):
        output = []
        visited = np.zeros_like(self.map)

        for x in range(self.width):
            for y in range(self.height):
                if (visited[x][y] == 1):
                    continue

                region = np.zeros_like(self.map)

                self.getTileRegion(x, y, region)

                visited[region == 1] = 1

                region_size = np.sum(region)

                if (region_size != 0):
                    output.append((region_size, region))

        output = sorted(output, key=lambda x: x[0])

        for _, region in output[:-1]:
            self.map[region == 1] = 1

    def getTileRegion(self, x, y, visited, tile_type=0):

        if (not self.is_within_bound(self.map, x, y) or visited[x][y] == 1 or self.map[x][y] != tile_type):
            return

        visited[x][y] = 1

        for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            self.getTileRegion(x+dx, y+dy, visited)

    def getRandomTile(self, tile_type=0) -> Coord:
        while (True):
            x = np.random.choice(range(self.width))
            y = np.random.choice(range(self.height))

            if (self.map[x][y] == tile_type):
                return Coord(x, y)

    def get_adjacent_neighbour(self, x, y):
        wall_count = 0

        for dx in range(2):
            for dy in range(2):

                if self.is_within_bound(self.map, x-dx, y-dy):
                    wall_count += self.map[x-dx][y-dy]
                else:
                    wall_count += 1

        return wall_count

    def is_within_bound(self, X: np.ndarray, x, y):
        width, height = X.shape

        return x >= 0 and y >= 0 and x < width and y < height

    def populateProp(self):
        player = None
        door = None

        for x in range(self.width):
            for y in range(self.height):
                if self.map[x][y] == 0:
                    if player is None:
                        player = Coord(x, y)

                    door = Coord(x, y)

        self.map[player.x][player.y] = 2
        self.map[door.x][door.y] = 4

        key = self.getRandomTile()
        self.map[key.x][key.y] = 3

        # Populate bat
        for _ in range(0):
            coord = self.getRandomTile()
            self.map[coord.x][coord.y] = 5

        # Populate scorpion
        for _ in range(0):
            coord = self.getRandomTile()
            self.map[coord.x][coord.y] = 6

        # Populate spider
        for _ in range(2):
            coord = self.getRandomTile()
            self.map[coord.x][coord.y] = 7
