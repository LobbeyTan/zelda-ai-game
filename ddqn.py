import argparse
import time
import sys
import torch
import json
import os
from datetime import datetime
from games.envs.reinforce import *

sys.setrecursionlimit(10000)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="DDQN method in solving zelda")

    parser.add_argument('--map_gen', choices=['CA', 'NF'], default='CA',
                        help="Map generation algorithm. [CA: Cellular Automata,  NF: Noice Fractal]")

    parser.add_argument('--width', type=int, default=64, help="The width of the map")
    parser.add_argument('--height', type=int, default=64, help="The height of the map")
    parser.add_argument('--n_spider', type=int, default=0, help="Number of spiders")
    parser.add_argument('--n_scorpion', type=int, default=0, help="Number of scorpions")
    parser.add_argument('--n_bat', type=int, default=0, help="Number of bats")
    parser.add_argument('--seed', type=int, default=2023, help="Random seed value")
    parser.add_argument('--delay', type=float, default=0.25, help="Delay of player moving")
    parser.add_argument('--train', type=int, default=1, help="Training DDQN Model")
    parser.add_argument('--model_path', type=str, default=None, help="Model loading path")
    parser.add_argument('--param_path', type=str, default=None, help="Parameters loading path")

    # Training hyperparameter
    parser.add_argument('--n_episode', type=int, default=40000, help="Number of training episodes")
    parser.add_argument('--save_every', type=int, default=500000, help="Number of training episodes")
    parser.add_argument('--exp_decay_rate', type=float, default=0.99999975, help="Exploration decay rate")

    args = parser.parse_args()
    train = bool(args.train)
    save_dir = ("temp/" if not train else "checkpoint/") + datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    if train:
        os.makedirs(save_dir)
        
        with open(save_dir+'/param.json', 'w') as file:
            json.dump(vars(args), file, indent=4)

    else:
        if args.param_path is not None:
            with open(args.param_path) as file:
                params = json.load(file)
            args.width = params['width']
            args.height = params['height']
            args.n_spider = params['n_spider']
            args.n_scorpion = params['n_scorpion']
            args.n_bat = params['n_bat']
            args.seed = params['seed']

    print(json.dumps(vars(args), indent=4))

    env = ZeldaReinforceEnv(args.width, args.height, args.map_gen, args.n_spider, args.n_scorpion, args.n_bat)
    env.seed(args.seed)

    state = env.reset(new_map=True)

    use_cuda = torch.cuda.is_available()

    print(f"Using CUDA: {use_cuda}")
    print("Is Training:", train)

    player = Player(n_states=env._map.size, n_actions=4, save_dir=save_dir, rand=env._prob._random,
                    exploration_rate_decay=args.exp_decay_rate, save_every=args.save_every)

    if args.model_path is not None:
        player.load(args.model_path, device="cuda" if use_cuda else "cpu")

    logger = MetricLogger(save_dir)

    episodes = args.n_episode
    for e in range(episodes):

        # Play the game!
        while True:

            # Run agent on the state
            action = player.act(state)

            # Agent performs action
            next_state, reward, done = env.step(action)

            if not train:
                env.render()
                time.sleep(args.delay)

            # Remember
            player.cache(state, next_state, action, reward, done)

            # Learn
            q, loss = player.learn()

            # Logging
            logger.log_step(reward, loss, q, env.key is None and env.door is None)

            # Update state
            state = next_state

            # Check if end of game
            if done:
                score = env.get_score()
                print("Total Score:", score)
                state = env.reset()
                break

        logger.log_episode()

        if (e+1) % 20 == 0:
            logger.record(episode=e+1, epsilon=player.exploration_rate, step=player.curr_step)

    player.save("zelda_net_trained.chkpt")
