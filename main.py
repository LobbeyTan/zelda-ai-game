
import time
from datetime import datetime
from games.envs.reinforce import *
from games.envs import ZeldaEnv
import sys
import torch


sys.setrecursionlimit(10000)


def playZeldaWithAstar():
    env = ZeldaEnv()
    obs = env.reset()

    for i in range(1000):
        env.run()
        env.render()

        time.sleep(0.25)


def playZeldaWithDDQN():
    env = ZeldaReinforceEnv()
    env.seed(2023)
    
    state = env.reset(new_map=True)

    use_cuda = torch.cuda.is_available()

    print(f"Using CUDA: {use_cuda}")
    print()

    save_dir = "checkpoint/" + datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    player = Player(n_states=env._map.size, n_actions=4, save_dir=save_dir, rand=env._prob._random)

    logger = MetricLogger(save_dir)

    episodes = 40000
    for e in range(episodes):

        # Play the game!
        while True:

            # Run agent on the state
            action = player.act(state)

            # Agent performs action
            next_state, reward, done = env.step(action)

            # Remember
            player.cache(state, next_state, action, reward, done)

            # Learn
            q, loss = player.learn()

            # Logging
            logger.log_step(reward, loss, q)

            # Update state
            state = next_state

            # Check if end of game
            if done:
                state = env.reset()
                break

        logger.log_episode()

        if e % 20 == 0:
            logger.record(episode=e, epsilon=player.exploration_rate, step=player.curr_step)
            

def test():
    env = ZeldaReinforceEnv()
    env.seed(2023)
    env.reset(new_map=True)
    
    for _ in range(10000):
        next_state, reward, done = env.step(env._prob._random.choice(4))
        
        time.sleep(0.25)
        if (done or _ % 20 == 0):
            env.reset()
        
        


if __name__ == '__main__':
    playZeldaWithDDQN()
    # env.reset()
