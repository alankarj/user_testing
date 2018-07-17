import json
import numpy as np
from src import config


class RLAgent:
    def __init__(self, params):
        self.params = params
        self.agent_actions_map = config.get_agent_actions_map()
        self.user_actions_map = config.get_user_actions_map()
        self.cs_map = config.get_cs_map()
        self.state_slots_map = config.get_state_slots_map()

    def next(self, state):
        task_state = state[config.TASK_STATE_STR]
        self.get_task_state_representation(task_state)

    def get_task_state_representation(self, state):

        # Get agent ts, cs representation
        agent_df = state[config.AGENT_DF_STR]
        agent_ts_rep = self.get_ts_rep(agent_df, self.agent_actions_map)
        agent_cs_rep = self.get_rep(self.cs_map, agent_df[config.CS_STR])

        # Get user ts, cs representation
        user_df = state[config.USER_DF_STR]
        user_ts_rep = self.get_ts_rep(user_df, self.user_actions_map)
        user_cs_rep = self.get_rep(self.cs_map, agent_df[config.CS_STR])

        # Get agent ACK cs representation
        agent_ack_cs_rep = self.get_rep(self.cs_map, state[config.AGENT_ACK_DF_STR][config.CS_STR])

        # Get recos representation
        recos = state[config.RECOS_STR]
        recos_rep = np.zeros((config.MAX_RECOS + 1))
        recos_rep[recos] = 1

        # Get slots representation (filled/not-filled)
        state_slots = list(self.state_slots_map.keys())
        state_slots_rep = np.zeros((len(state_slots)))
        for slot in state_slots:
            if state[slot] != '':
                state_slots_rep[self.state_slots_map[slot]] = 1

        full_state_rep = np.hstack((agent_ts_rep, agent_cs_rep, user_ts_rep, user_cs_rep,
                                    agent_ack_cs_rep, recos_rep, state_slots_rep))

        if self.params.print_info == 2:
            print("State: ", json.dumps(state, indent=2))
            print("Agent TS rep: ", agent_ts_rep)
            print("Agent CS rep: ", agent_cs_rep)
            print("User TS rep: ", user_ts_rep)
            print("User CS rep: ", user_cs_rep)
            print("Agent ACK CS rep: ", agent_ack_cs_rep)
            print("Recos rep: ", recos_rep)
            print("State slots rep: ", state_slots_rep)
            print("Full state rep size: ", np.shape(full_state_rep))

        return full_state_rep

    def prepare_training_data(self):
        params = self.params
        dialog_list = params.dialog_list
        X_list = []
        Y_list = []
        for dialog in dialog_list:
            for turn in dialog:
                state = dialog[turn][config.AGENT_STR][config.PREV_STATE_STR][config.TASK_STATE_STR]
                X_list.append(self.get_task_state_representation(state))
                Y_list.append(self.get_ts_rep(dialog[turn][config.AGENT_STR][config.AGENT_DF_STR], self.agent_actions_map))
        print(np.shape(np.array(X_list)))
        print(np.shape(np.array(Y_list)))

    def get_ts_rep(self, action_df, dictionary):
        ts_string, _ = config.deconstruct_ts(action_df[config.TS_STR])
        return self.get_rep(dictionary, ts_string)

    @staticmethod
    def get_rep(dictionary, key):
        rep = np.zeros((len(list(dictionary.keys()))))
        rep[dictionary[key]] = 1
        return rep
