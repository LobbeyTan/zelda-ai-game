from games.envs.probs.binary_prob import BinaryProblem
from games.envs.probs.ddave_prob import DDaveProblem
from games.envs.probs.mdungeon_prob import MDungeonProblem
from games.envs.probs.sokoban_prob import SokobanProblem
from games.envs.probs.zelda_prob import ZeldaProblem
from games.envs.probs.smb_prob import SMBProblem
from games.envs.probs.problem import Problem

# all the problems should be defined here with its corresponding class
PROBLEMS: dict[str, Problem] = {
    "binary": BinaryProblem,
    "ddave": DDaveProblem,
    "mdungeon": MDungeonProblem,
    "sokoban": SokobanProblem,
    "zelda": ZeldaProblem,
    "smb": SMBProblem
}
