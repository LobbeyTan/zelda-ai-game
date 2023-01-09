
import time
from games.envs import ZeldaEnv
import numpy as np
from gym.utils import seeding
import sys

sys.setrecursionlimit(10000)

if __name__ == '__main__':
    env = ZeldaEnv()
    obs = env.reset()

    for i in range(1000):
        env.run()
        env.render()
        
        # time.sleep(0.25)
        
        # env.reset()
