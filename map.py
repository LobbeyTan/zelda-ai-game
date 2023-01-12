import argparse
import time
import sys
import json
from games.envs import ZeldaEnv

sys.setrecursionlimit(10000)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Map generation showcase")

    parser.add_argument('--map_gen', choices=['CA', 'NF'], default='CA',
                        help="Map generation algorithm. [CA: Cellular Automata,  NF: Noice Fractal]")

    parser.add_argument('--width', type=int, default=64, help="The width of the map")
    parser.add_argument('--height', type=int, default=64, help="The height of the map")
    parser.add_argument('--n_spider', type=int, default=6, help="Number of spiders")
    parser.add_argument('--n_scorpion', type=int, default=6, help="Number of scorpions")
    parser.add_argument('--n_bat', type=int, default=6, help="Number of bats")
    parser.add_argument('--seed', type=int, default=2024, help="Random seed value")
    parser.add_argument('--delay', type=float, default=5, help="Delay of player moving")

    args = parser.parse_args()
    print(json.dumps(vars(args), indent=4))

    env = ZeldaEnv(args.width, args.height, args.map_gen, args.n_spider, args.n_scorpion, args.n_bat)
    env.seed(args.seed)

    obs = env.reset()

    while True:
        try:
            env.render()

            time.sleep(args.delay)
            
            env.reset()
        except:
            break
