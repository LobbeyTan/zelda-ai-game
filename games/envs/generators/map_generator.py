import numpy as np
from collections import namedtuple
import sys

Coord = namedtuple("Coord", ["x", "y"])


class MapGenerator:

    def __init__(self, rand: np.random, width: int, height: int, props: dict, p: float) -> None:
        self.map = None
        self.rand = rand
        self.width = width
        self.height = height
        self.area = width * height
        self.props = props
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
        cnt = 1
        regions = np.zeros_like(self.map)

        for x in range(self.width):
            for y in range(self.height):
                if (regions[x][y] != 0):
                    continue

                visited = np.zeros_like(self.map)

                self.getTileRegion(x, y, visited)

                regions[visited != 0] = cnt

                region_size = np.sum(visited != 0)

                if (region_size != 0):
                    output.append((region_size, visited))
                    cnt += 1

        output = sorted(output, key=lambda x: x[0])

        for size, region in output[:-1]:
            if (size > (self.area / 20)):
                self.connectRegion(region, output[-1][1])
            else:
                self.map[region != 0] = 1

    def connectRegion(self, r1, r2):
        r1_bound = self.getBoundaryCoords(r1)
        r2_bound = self.getBoundaryCoords(r2)

        min_dist = sys.maxsize
        min_points = None
        for c1 in r1_bound:
            for c2 in r2_bound:
                dist = abs(c1.x - c2.x) + abs(c1.y - c2.y)
                if dist < min_dist:
                    min_dist = dist
                    min_points = (c1, c2)

        path = self.getConnectedPath(*min_points)

    def getConnectedPath(self, c1: Coord, c2: Coord) -> list[Coord]:
        path = []
        x1 = c1.x
        y1 = c1.y
        x2 = c2.x
        y2 = c2.y

        while (x1 != x2 or y1 != y2):
            dx = x1 - x2
            dy = y1 - y2

            if dx != 0:
                x1 += -1 if dx > 0 else 1

            if dy != 0:
                y1 += -1 if dy > 0 else 1

            path.append(Coord(x1, y1))
            self.map[x1][y1] = 0  # Change to empty tiles
            self.fill_adjacent_tile(x1, y1, tile_type=0)  # Change adjacent to empty tiles

        return path

    def getBoundaryCoords(self, region) -> list[Coord]:
        boundaries = []
        for x in range(self.width):
            for y in range(self.height):
                if region[x][y] == 5:
                    boundaries.append(Coord(x, y))

        return boundaries

    def getTileRegion(self, x, y, visited, last_move=(0, 0)):

        if (self.is_within_bound(self.map, x, y) and self.map[x][y] != 0 and last_move != (0, 0)):
            visited[x-last_move[0]][y-last_move[1]] = 5  # boundary

        if (not self.is_within_bound(self.map, x, y) or visited[x][y] != 0 or self.map[x][y] != 0):
            return

        visited[x][y] = 1

        for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            self.getTileRegion(x+dx, y+dy, visited, last_move=(dx, dy))

    def getRandomTile(self, tile_type=0) -> Coord:
        while (True):
            x = self.rand.choice(range(self.width))
            y = self.rand.choice(range(self.height))

            if (self.map[x][y] == tile_type):
                return Coord(x, y)

    def fill_adjacent_tile(self, x, y, tile_type=0):
        for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            if self.is_within_bound(self.map, x+dx, y+dy):
                self.map[x+dx][y+dy] = tile_type

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
        for _ in range(self.props['bat']):
            coord = self.getRandomTile()
            self.map[coord.x][coord.y] = 5

        # Populate scorpion
        for _ in range(self.props['scorpion']):
            coord = self.getRandomTile()
            self.map[coord.x][coord.y] = 6

        # Populate spider
        for _ in range(self.props['spider']):
            coord = self.getRandomTile()
            self.map[coord.x][coord.y] = 7
