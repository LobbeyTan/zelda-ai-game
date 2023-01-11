from torch import nn
import copy
import torch


class ZeldaNet(nn.Module):

    def __init__(self, n_states, n_actions) -> None:
        super().__init__()

        self.online = nn.Sequential(
            nn.Linear(n_states, 1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, n_actions)
        )

        self.target = copy.deepcopy(self.online)

        for p in self.target.parameters():
            p.requires_grad = False

    def forward(self, input: torch.Tensor, model):
        # print('Before:', input.shape)

        if input.ndim == 2:
            input = input.unsqueeze(dim=0)

        input = input.flatten(start_dim=1, end_dim=-1)
        input = input.float()

        # print('After:', input.shape)

        if model == 'online':
            return self.online(input)

        if model == 'target':
            return self.target(input)
