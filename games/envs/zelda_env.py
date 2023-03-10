from games.envs.probs import PROBLEMS
from games.envs.reps import REPRESENTATIONS
from games.envs.reps.narrow_rep import NarrowRepresentation
from games.envs.probs.zelda_prob import ZeldaProblem
from games.envs.models import CREATURES
from games.envs.models.movable import Movable
from games.envs.models.constant import Coord
from games.envs.helper import get_int_prob, get_string_map
import numpy as np
import gym
from gym import spaces
import PIL
from games.envs.astar import Astar
"""
The Zelda GYM Environment
"""


class ZeldaEnv(gym.Env):
    """
    The type of supported rendering
    """
    metadata = {'render.modes': ['human', 'rgb_array']}

    """
    Constructor for the interface.

    Parameters:
        prob (string): the current problem. This name has to be defined in PROBLEMS
        constant in gym_pcgrl.envs.probs.__init__.py file
        rep (string): the current representation. This name has to be defined in REPRESENTATIONS
        constant in gym_pcgrl.envs.reps.__init__.py
    """

    def __init__(self, width: int, height: int, map_gen='CA', n_spider=0, n_scorpion=0, n_bat=0, show_grid=False):
        self._prob = ZeldaProblem(width, height)
        self._rep = NarrowRepresentation(
            show_grid=show_grid,
            gen_type=map_gen,
            props={
                'spider': n_spider,
                'bat': n_bat,
                'scorpion': n_scorpion,
            }
        )
        self.creatures: list[Movable] = []
        self._rep_stats = None
        self._iteration = 0
        self._changes = 0
        self._total_steps = 0
        self.player = 0
        self._max_changes = max(int(0.2 * self._prob._width * self._prob._height), 1)
        self._max_iterations = self._max_changes * self._prob._width * self._prob._height
        self._heatmap = np.zeros((self._prob._height, self._prob._width))

        self.seed()
        self.viewer = None

        self.action_space = self._rep.get_action_space(self._prob._width, self._prob._height, self.get_num_tiles())
        self.observation_space = self._rep.get_observation_space(self._prob._width, self._prob._height, self.get_num_tiles())
        self.observation_space.spaces['heatmap'] = spaces.Box(
            low=0, high=self._max_changes, dtype=np.uint8, shape=(self._prob._height, self._prob._width))

    """
    Seeding the used random variable to get the same result. If the seed is None,
    it will seed it with random start.

    Parameters:
        seed (int): the starting seed, if it is None a random seed number is used.

    Returns:
        int[]: An array of 1 element (the used seed)
    """

    def seed(self, seed=None):
        seed = self._rep.seed(seed)
        self._prob.seed(seed)
        return [seed]

    """
    Resets the environment to the start state

    Returns:
        Observation: the current starting observation have structure defined by
        the Observation Space
    """

    def reset(self):
        self._changes = 0
        self._iteration = 0
        self._total_steps = 0
        self._rep.reset(self._prob._width, self._prob._height, get_int_prob(self._prob._prob, self._prob.get_tile_types()))
        self.initialize_creatures()

        self._rep_stats = self._prob.get_stats(get_string_map(self._rep._map, self._prob.get_tile_types()))
        self._prob.reset(self._rep_stats)
        self._heatmap = np.zeros((self._prob._height, self._prob._width))

        observation = self._rep.get_observation()
        observation["heatmap"] = self._heatmap.copy()

        self._map = self._rep._map.copy()
        self.player = self.get_tile_coords(2)[0]
        return observation

    def get_score(self):
        print("Steps:", self._total_steps)
        key = self.get_tile_coords(3)
        door = self.get_tile_coords(4)

        loss = len(key) != 0 or len(door) != 0

        key_reward = (1 / (self.manhattan_distance([self.player], key) + 1)) * 50
        door_reward = (1 / (self.manhattan_distance([self.player], door) + 1)) * 100
        loss_penalty = int(loss) * - 100

        score = self._total_steps * -0.5 + key_reward + door_reward + loss_penalty

        return score

    def manhattan_distance(self, pos_1: list[Coord], pos_2: list[Coord]):
        if len(pos_1) == 0 or len(pos_2) == 0:
            return 0

        total_distance = 0

        for c1 in pos_1:
            total_distance += sum([abs(c1.x - c2.x) + abs(c1.y - c2.y) for c2 in pos_2]) / len(pos_2)

        return total_distance / len(pos_1)

    def get_map(self):
        return self._rep._map

    def get_tile_coords(self, tile_type=0) -> Coord:
        rows, cols = np.where(self._rep._map == tile_type)

        return [Coord(x, y) for x, y in zip(rows, cols)]

    def initialize_creatures(self):
        _map = self.get_map()

        for x in range(_map.shape[0]):
            for y in range(_map.shape[1]):
                if _map[x, y] in list(CREATURES.keys()):
                    self.creatures.append(CREATURES[_map[x, y]](_map, Coord(x, y)))

    """
    Get the border tile that can be used for padding

    Returns:
        int: the tile number that can be used for padding
    """

    def get_border_tile(self):
        return self._prob.get_tile_types().index(self._prob._border_tile)

    """
    Get the number of different type of tiles that are allowed in the observation

    Returns:
        int: the number of different tiles
    """

    def get_num_tiles(self):
        return len(self._prob.get_tile_types())

    """
    Adjust the used parameters by the problem or representation

    Parameters:
        change_percentage (float): a value between 0 and 1 that determine the
        percentage of tiles the algorithm is allowed to modify. Having small
        values encourage the agent to learn to react to the input screen.
        **kwargs (dict(string,any)): the defined parameters depend on the used
        representation and the used problem
    """

    def adjust_param(self, **kwargs):
        if 'change_percentage' in kwargs:
            percentage = min(1, max(0, kwargs.get('change_percentage')))
            self._max_changes = max(int(percentage * self._prob._width * self._prob._height), 1)
        self._max_iterations = self._max_changes * self._prob._width * self._prob._height
        self._prob.adjust_param(**kwargs)
        self._rep.adjust_param(**kwargs)
        self.action_space = self._rep.get_action_space(self._prob._width, self._prob._height, self.get_num_tiles())
        self.observation_space = self._rep.get_observation_space(self._prob._width, self._prob._height, self.get_num_tiles())
        self.observation_space.spaces['heatmap'] = spaces.Box(
            low=0, high=self._max_changes, dtype=np.uint8, shape=(self._prob._height, self._prob._width))

    """
    Advance the environment using a specific action

    Parameters:
        action: an action that is used to advance the environment (same as action space)

    Returns:
        observation: the current observation after applying the action
        float: the reward that happened because of applying that action
        boolean: if the problem eneded (episode is over)
        dictionary: debug information that might be useful to understand what's happening
    """

    def step(self, action):
        self._iteration += 1

        # save copy of the old stats to calculate the reward
        old_stats = self._rep_stats
        # update the current state to the new state based on the taken action
        change, x, y = self._rep.update(action)
        if change > 0:
            self._changes += change
            self._heatmap[y][x] += 1.0
            self._rep_stats = self._prob.get_stats(get_string_map(self._rep._map, self._prob.get_tile_types()))
        # calculate the values
        observation = self._rep.get_observation()
        observation["heatmap"] = self._heatmap.copy()
        reward = self._prob.get_reward(self._rep_stats, old_stats)
        done = self._prob.get_episode_over(
            self._rep_stats, old_stats) or self._changes >= self._max_changes or self._iteration >= self._max_iterations
        info = self._prob.get_debug_info(self._rep_stats, old_stats)
        info["iterations"] = self._iteration
        info["changes"] = self._changes
        info["max_iterations"] = self._max_iterations
        info["max_changes"] = self._max_changes
        # return the values
        return observation, reward, done, info

    def run(self):
        self._total_steps += 1
        self._rep._map[self._rep._map == 8] = 0

        for c in self.creatures:
            c.step()

        astar = Astar(self._rep._map)
        # print(astar.getNextMove())
        astar.step()

        next_player_coord = self.get_tile_coords(2)
        if len(next_player_coord) != 0:
            self.player = next_player_coord[0]

    """
    Render the current state of the environment

    Parameters:
        mode (string): the value has to be defined in render.modes in metadata

    Returns:
        img or boolean: img for rgb_array rendering and boolean for human rendering
    """

    def render(self, mode='human'):
        tile_size = 16
        img = self._prob.render(get_string_map(self._rep._map, self._prob.get_tile_types()))
        img = self._rep.render(img, self._prob._tile_size, self._prob._border_size).convert("RGB")
        if mode == 'rgb_array':
            return img
        elif mode == 'human':
            from gym.envs.classic_control import rendering
            if self.viewer is None:
                self.viewer = rendering.SimpleImageViewer()
            if not hasattr(img, 'shape'):
                img = np.array(img)
            self.viewer.imshow(img)
            return self.viewer.isopen

    """
    Close the environment
    """

    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None
