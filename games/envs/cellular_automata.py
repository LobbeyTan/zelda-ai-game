import numpy as np
from scipy.signal import convolve2d
from collections import namedtuple

Coord = namedtuple("Coord", ["x", "y"])


def ca_step_conv(X):
    """Evolve the maze by a single CA step."""

    K = np.ones((3, 3))
    n = convolve2d(X, K, mode='same', boundary='wrap') - X
    return (n == 3) | (X & ((n > 0) & (n < 6)))


def ca_step(X: np.ndarray, threshold=4):
    """Evolve the maze by a single CA step."""

    width, height = X.shape

    tmp = X.copy()

    for x in range(width):
        for y in range(height):
            neighbour_wall = get_all_neighbour(X, x, y)

            tmp[x][y] = int(neighbour_wall > threshold)

    return tmp


def process(X: np.ndarray):
    output = []
    visited = np.zeros_like(X)

    for x in range(X.shape[0]):
        for y in range(X.shape[1]):
            if (visited[x][y] == 1):
                continue

            region = np.zeros_like(X)

            getTileRegion(x, y, X, region)

            visited[region == 1] = 1

            region_size = np.sum(region)

            if (region_size != 0):
                output.append((region_size, region))

    output = sorted(output, key=lambda x: x[0])

    for _, region in output[:-1]:
        X[region == 1] = 1

    return X


def getTileRegion(x, y, map, visited, tile_type=0):

    if (not is_within_bound(map, x, y) or visited[x][y] == 1 or map[x][y] != tile_type):
        return

    visited[x][y] = 1

    for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
        getTileRegion(x+dx, y+dy, map, visited)


def getRandomTile(X, tile_type=0) -> Coord:
    while (True):
        x = np.random.choice(range(X.shape[0]))
        y = np.random.choice(range(X.shape[1]))

        if (X[x][y] == tile_type):
            return Coord(x, y)


def get_all_neighbour(X: np.ndarray, x, y):
    wall_count = 0

    for dx in range(x-1, x+2):
        for dy in range(y-1, y+2):

            if is_within_bound(X, dx, dy):
                if (not (dx == x and dy == y)):
                    wall_count += X[dx][dy]
            else:
                wall_count += 1

    return wall_count


def get_adjacent_neighbour(X: np.ndarray, x, y):
    wall_count = 0

    for dx in range(2):
        for dy in range(2):

            if is_within_bound(X, x-dx, y-dy):
                wall_count += X[x-dx][y-dy]
            else:
                wall_count += 1

    return wall_count


def is_within_bound(X: np.ndarray, dx, dy):
    width, height = X.shape
    return dx >= 0 and dy >= 0 and dx < width and dy < height


def populateProp(rand: np.random, map: np.ndarray):
    width, height = map.shape

    player = None
    door = None

    for x in range(width):
        for y in range(height):
            if map[x][y] == 0:
                if player is None:
                    player = Coord(x, y)

                door = Coord(x, y)

    map[player.x][player.y] = 2
    map[door.x][door.y] = 4

    key = getRandomTile(map)
    map[key.x][key.y] = 3

    # Populate bat
    for _ in range(0):
        coord = getRandomTile(map)
        map[coord.x][coord.y] = 5

    # Populate scorpion
    for _ in range(0):
        coord = getRandomTile(map)
        map[coord.x][coord.y] = 6

    # Populate spider
    for _ in range(2):
        coord = getRandomTile(map)
        map[coord.x][coord.y] = 7


def generate_CA_map(rand: np.random, width: int, height: int, prob: dict[str, float]):
    # 0: Empty
    # 1: Wall

    p = .55
    map = rand.choice([0, 1], size=(width, height), p=[1-p, p])

    for _ in range(2):
        map = ca_step(map)

    map = process(map)

    populateProp(rand, map)

    return map
