
import time
from games.envs import ZeldaEnv
from games.envs.fractal_generator import FractorMapGenerator
import numpy as np
from gym.utils import seeding

if __name__ == '__main__':
    # env = ZeldaEnv()
    # obs = env.reset()

    # for i in range(1000):
    #     env.run()
    #     env.render()
        
    #     time.sleep(0.25)

    _random, seed = seeding.np_random()
    g = FractorMapGenerator(_random, 100, 100)
    g.generateMap()
