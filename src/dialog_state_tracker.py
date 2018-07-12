from src import config


class StateTracker:
    def __init__(self, params):
        self.params = params
        self.state = {config.TASK_STATE_STR: None, config.SOCIAL_STATE_STR: None}

    def reset(self):
        task_state = {}
        for inf_slot in config.INFORMABLE_SLOTS + config.INFORMABLE_SLOTS_PSEUDO:
            task_state[inf_slot] = ''
        task_state[config.TURN_STR] = 0
        task_state[config.PREV_AGENT_DF_STR] = config.BLANK_DF
        task_state[config.PREV_USER_DF_STR] = config.BLANK_DF
        task_state[config.AGENT_DF_STR] = config.BLANK_DF
        task_state[config.USER_DF_STR] = config.BLANK_DF
        self.state[config.TASK_STATE_STR] = task_state
        return self.state

    def step(self, user_df, agent_df):
        task_state = self.state[config.TASK_STATE_STR]
        for inf_slot in config.INFORMABLE_SLOTS + config.INFORMABLE_SLOTS_PSEUDO:
            task_state[inf_slot] = user_df[config.VALUE_STR]
        task_state[config.TURN_STR] += 1
        task_state[config.PREV_AGENT_DF_STR] = task_state[config.AGENT_DF_STR]
        task_state[config.PREV_USER_DF_STR] = task_state[config.USER_DF_STR]
        task_state[config.AGENT_DF_STR] = user_df
        task_state[config.USER_DF_STR] = agent_df
        self.state[config.TASK_STATE_STR] = task_state
        return self.state
