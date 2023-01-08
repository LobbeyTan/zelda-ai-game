from gym.envs.registration import register
from games.envs.probs import PROBLEMS
from games.envs.reps import REPRESENTATIONS

# Register all the problems with every different representation for the OpenAI GYM
for prob in PROBLEMS.keys():
    for rep in REPRESENTATIONS.keys():
        register(
            id='{}-{}-v0'.format(prob, rep),
            entry_point='games.envs:GameEnv',
            kwargs={"prob": prob, "rep": rep}
        )
