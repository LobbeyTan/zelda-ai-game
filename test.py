import numpy as np

map = [[1, 0, 0, 0, 0, 1, 0, 1, 3, 1],
       [0, 0, 0, 0, 0, 1, 1, 0, 0, 1],
       [1, 0, 0, 0, 0, 1, 0, 1, 0, 1],
       [0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
       [1, 1, 1, 0, 1, 0, 1, 0, 0, 1],
       [0, 1, 0, 1, 1, 1, 0, 0, 0, 0],
       [1, 1, 0, 1, 0, 1, 0, 4, 0, 1],
       [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
       [1, 0, 0, 4, 0, 1, 0, 0, 0, 0],
       [2, 0, 1, 0, 0, 0, 0, 1, 0, 1],]


def is_within_bound(X: np.ndarray, dx, dy):
    width, height = X.shape
    return dx >= 0 and dy >= 0 and dx < width and dy < height


def getRegion(x, y, map, visited, tile_type=0):
    if (not is_within_bound(map, x, y) or visited[x][y] == 1 or map[x][y] != tile_type):
        return

    visited[x][y] = 1
    
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            getRegion(x+dx, y+dy, map, visited)


map = np.array(map)

visited = np.zeros_like(map)

getRegion(1, 0, map, visited)

print(visited)
