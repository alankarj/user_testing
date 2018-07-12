import numpy as np
import json
import os
import pickle
import random
from src import config


class UserSimulator:
    def __init__(self, params, user_simulator_reasoner):
        self.params = params
        self.reasoner = user_simulator_reasoner
        self.user_profile = None
        self.slot_values = None
        self.agenda = None

    def reset(self):
        self.user_profile = self.generate_user_profile()
        self.slot_values = self.get_slot_values()
        self.agenda = self.generate_user_agenda()

    def generate_user_profile(self):
        params = self.params
        user_profile = {}
        prob_user_profile = config.get_prob_user_profile()

        if params.command_line_user == 0:
            print("Spawning new user profile.")
            for k in prob_user_profile.keys():
                if type(prob_user_profile[k]) is dict:
                    keys = list(prob_user_profile[k].keys())
                    values = list(prob_user_profile[k].values())
                    # Pick a value based on multinomial distribution.
                    user_profile[k] = keys[np.argwhere(np.random.multinomial(1, values) == 1)[0][0]]

        else:
            for k in prob_user_profile.keys():
                user_profile[k] = getattr(params, k)

        print(json.dumps(user_profile, indent=2))
        return user_profile

    def generate_user_agenda(self):
        user_agenda = []
        print("Constructing new user agenda.")
        if self.user_profile[config.INITIATIVE_TYPE_STR] == config.INITIATIVE_TYPES[0]:
            keys = list(config.PROB_USER_BEHAVIOUR[config.INFORM_STR + '_' + config.SLOT_STR].keys())
            values = list(config.PROB_USER_BEHAVIOUR[config.INFORM_STR + '_' + config.SLOT_STR].values())

            slot = keys[np.argwhere(np.random.multinomial(1, values) == 1)[0][0]]
            value = self.slot_values[slot]

            ts = config.construct_ts(config.INFORM_STR, slot, value)
            # Hedging if I-type, else NONE.
            cs = config.ALL_CONV_STRATEGIES[2] if self.user_profile[config.CONV_GOAL_TYPE_STR] == config.CONV_GOAL_TYPES[0] else config.ALL_CONV_STRATEGIES[-1]
            user_agenda.append({config.TS_STR: ts, config.CS_STR: cs})

        # Always end with a bye + NONE.
        user_agenda.append({config.TS_STR: config.construct_ts(config.NON_REQINF_USER_TS[-1]), config.CS_STR: config.ALL_CONV_STRATEGIES[-1]})
        print(json.dumps(user_agenda, indent=2))
        return user_agenda

    def get_slot_values(self):
        print("Getting new slot values.")
        params = self.params
        slot_values = {}
        for inf_slot in config.INFORMABLE_SLOTS:
            # If the user has single preference for an inform slot, sample uniformly at random from the list of slot values.
            if self.user_profile[inf_slot + config.SLOT_PREFERENCE_TYPE_STR] == config.SLOT_PREFERENCE_TYPES[0]:
                with open(os.path.join(params.lexicons_folder_path, inf_slot + config.SLOT_LISTS_FILE_SUFFIX), 'rb') as f:
                    full_list = pickle.load(f)
                slot_values[inf_slot] = random.sample(full_list, 1)[0]
        print(json.dumps(slot_values, indent=2))
        return slot_values

    # def next(self, state, agent_action):
    #     ts_list = list(self.reasoner[agent_action].keys())
    #     ts_string = self.task_reasoner(state, ts_list)
    #     cs_list = self.reasoner[agent_action][ts_string]
    #     return ts_string, self.social_reasoner[cs_list]
    #
    # def task_reasoner(self, state, ts_list):


    def social_reasoner(self, cs_list):
        params = self.params
        if params.conv_goal_type == config.CONV_GOAL_TYPES[0]:
            # I-type user!
            cs = random.sample(cs_list[1:], 1)[0]
        else:
            cs = cs_list[0]
        return cs
