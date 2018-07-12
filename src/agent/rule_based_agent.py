import random
from src import config


class RuleBasedAgent:
    def __init__(self, params, agent_reasoner):
        self.params = params
        self.reasoner = agent_reasoner

    def next(self, state):
        task_state = state[config.TASK_STATE_STR]
        print(task_state)
        #  Key changes to a triple only if affirm or negate (greater context required)
        if task_state[config.USER_DF_STR][config.TS_STR] not in [config.AFFIRM_STR, config.NEGATE_STR]:
            key = (config.deconstruct_ts(task_state[config.USER_DF_STR][config.TS_STR])[0], task_state[config.USER_DF_STR][config.CS_STR])
        else:
            key = (config.deconstruct_ts(task_state[config.PREV_AGENT_DF_STR][config.TS_STR])[0],
                   config.deconstruct_ts(task_state[config.USER_DF_STR][config.TS_STR])[0],
                   task_state[config.USER_DF_STR][config.CS_STR])

        ts_string = list(self.reasoner[key].keys())[0]
        cs_list = list(self.reasoner[key].values())[0]
        return ts_string, self.social_reasoner(cs_list)

    def task_reasoner(self):
        pass

    def social_reasoner(self, cs_list):
        params = self.params
        if params.agent_social_type == config.AGENT_SOCIAL_TYPE[0]:
            # Social agent!
            cs = random.sample(cs_list[1:], 1)[0]
        else:
            cs = cs_list[0]
        return cs
