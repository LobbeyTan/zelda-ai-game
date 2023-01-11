import torch
import numpy as np
from games.envs.reinforce.model import ZeldaNet
from collections import deque
import os


class Player:

    def __init__(self, n_states, n_actions, rand: np.random, save_dir='/checkpoint'):
        self.n_states = n_states
        self.n_actions = n_actions
        self.save_dir = save_dir
        self.rand = rand
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.net = ZeldaNet(self.n_states, self.n_actions)
        self.net.to(self.device)

        self.exploration_rate = 1
        self.exploration_rate_decay = 0.99999975
        self.exploration_rate_min = 0.1
        self.curr_step = 0
        self.save_every = 5e5

        self.memory = deque(maxlen=100000)
        self.batch_size = 32

        # Bellman Equation
        self.gamma = 0.9

        # Model Training
        self.optimizer = torch.optim.Adam(self.net.parameters(), lr=0.00025)
        self.loss_fn = torch.nn.SmoothL1Loss()

        # Learning parameters
        self.burnin = 1e4  # min. experiences before training
        self.learn_every = 3  # no. of experiences between updates to Q_online
        self.sync_every = 1e4  # no. of experiences between Q_target & Q_online sync

    def act(self, state: np.ndarray):

        if self.rand.random() <= self.exploration_rate:
            action_idx = self.rand.randint(self.n_actions)

        else:
            state = torch.tensor(state).to(self.device)
            action_values = self.net(state, model='online')
            action_idx = torch.argmax(action_values, axis=1).item()

        self.exploration_rate *= self.exploration_rate_decay
        self.exploration_rate = max(self.exploration_rate_min, self.exploration_rate)

        self.curr_step += 1
        return action_idx

    def cache(self, state, next_state, action, reward, done):
        state = torch.tensor(state).to(self.device)
        next_state = torch.tensor(next_state).to(self.device)
        action = torch.tensor(action).to(self.device)
        reward = torch.tensor(reward).to(self.device)
        done = torch.tensor(done).to(self.device)

        self.memory.append([state, next_state, action, reward, done])

    def recall(self):
        batch = [self.memory[idx] for idx in self.rand.choice(len(self.memory), size=self.batch_size)]

        state, next_state, action, reward, done = map(torch.stack, zip(*batch))

        return state, next_state, action.squeeze(), reward.squeeze(), done.squeeze()

    def td_estimate(self, state, action):
        current_Q = self.net(state, model='online')[np.arange(0, self.batch_size), action]

        return current_Q

    def td_target(self, reward, next_state, done):
        next_state_Q = self.net(next_state, model='online')
        best_action = torch.argmax(next_state_Q, axis=1)
        next_Q = self.net(next_state, model='target')[np.arange(0, self.batch_size), best_action]

        return (reward + (1 - done.float()) * self.gamma * next_Q).float()

    def update_Q_online(self, td_estimate, td_target):
        loss: torch.Tensor = self.loss_fn(td_estimate, td_target)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def sync_Q_target(self):
        self.net.target.load_state_dict(self.net.online.state_dict())

    def save(self):
        cwd = os.getcwd()
        fname = f"mario_net_{int(self.curr_step // self.save_every)}.chkpt"
        save_path = os.path.join(cwd, self.save_dir, "model", fname)

        try:
            os.makedirs(os.path.join(cwd, self.save_dir, "model"))
        except:
            pass

        torch.save(dict(model=self.net.state_dict(), exploration_rate=self.exploration_rate), save_path)

        print(f"MarioNet saved to {save_path} at step {self.curr_step}")

    def learn(self):
        if self.curr_step % self.sync_every == 0:
            self.sync_Q_target()

        if self.curr_step % self.save_every == 0:
            self.save()

        if self.curr_step < self.burnin:
            return None, None

        if self.curr_step % self.learn_every != 0:
            return None, None

        # Sample from memory
        state, next_state, action, reward, done = self.recall()

        # Get TD Estimate
        td_est = self.td_estimate(state, action)

        # Get TD Target
        td_tgt = self.td_target(reward, next_state, done)

        # Backpropagate loss through Q_online
        loss = self.update_Q_online(td_est, td_tgt)

        return (td_est.mean().item(), loss)

    @torch.no_grad()
    def predict(self, state: np.ndarray):
        state = torch.tensor(state).to(self.device)
        action_values = self.net(state, model='online')
        action_idx = torch.argmax(action_values, axis=1).item()
        
        return action_idx
    
    def load(self, path):
        save_dict = torch.load(path)
        
        self.net.load_state_dict(save_dict['model'])
        self.net.eval()