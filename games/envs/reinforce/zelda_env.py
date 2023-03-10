import numpy as np
from games.envs.zelda_env import ZeldaEnv
from games.envs.models.constant import Coord
from enum import Enum
from collections import namedtuple


ACTION_MAP = {
    0: (-1, 0),
    1: (0, -1),
    2: (1, 0),
    3: (0, 1),
}

Episode = namedtuple('Episode', ['next_state', 'reward', 'done'])


class ZeldaReinforceEnv(ZeldaEnv):

    def __init__(self, width: int, height: int, map_gen='CA', n_spider=0, n_scorpion=0, n_bat=0):
        super().__init__(width, height, map_gen, n_spider, n_scorpion, n_bat)

    def reset(self, new_map=False):
        self._total_steps = 0
        if new_map:
            super().reset()

        # Reset map (return all to initial positions)
        for x in range(self._prob._width):
            for y in range(self._prob._height):
                self._rep._map[x, y] = self._map[x, y]

        self.state = self._rep._map

        self.player: Coord = self.get_tile_coords(2)[0]
        self.key: Coord = self.get_tile_coords(3)[0]
        self.door: Coord = self.get_tile_coords(4)[0]
        self.empty_tiles: list[Coord] = self.get_tile_coords(0)

        for c in self.creatures:
            c.reset()

        return self.state.copy()

    def step(self, action) -> Episode:
        self._total_steps += 1

        for c in self.creatures:
            c.step()

        reward = 0
        eaten_by_creature = len(self.get_tile_coords(2)) == 0

        dx, dy = ACTION_MAP[action]
        next_pos = Coord(self.player.x + dx, self.player.y + dy)

        if eaten_by_creature:
            reward = -1
        elif not self.is_valid_action(action):
            reward = -0.5
        else:
            if next_pos == self.key:
                self.key = None
                reward = 1
            elif next_pos == self.door:
                self.door = None
                reward = 1
            elif next_pos in [c.current_coord for c in self.creatures]:
                reward = -1
                eaten_by_creature = True
            else:
                reward = -0.04

            self.state[self.player] = 0
            self.state[next_pos] = 2
            self.player = next_pos

        # Is game over if eaten by creature or completed the game
        done = eaten_by_creature or (self.key is None and self.door is None)

        return Episode(self.state.copy(), reward, done)

    def is_valid_action(self, action):
        x = self.player.x + ACTION_MAP[action][0]
        y = self.player.y + ACTION_MAP[action][1]
        w = self._prob._width
        h = self._prob._height

        return x >= 0 and y >= 0 and x < w and y < h and self.state[x][y] != 1 and not (self.key is not None and self.state[x][y] == 4)
