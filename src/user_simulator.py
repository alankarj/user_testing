import numpy as np
import json
import os
import pickle
import random


class UserSimulator:
    def __init__(self, params):
        self.params = params
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

        if params.command_line_user == 0:
            print("Spawning new user profile.")
            for k in params.prob_user_profile.keys():
                if type(params.prob_user_profile[k]) is dict:
                    keys = list(params.prob_user_profile[k].keys())
                    values = list(params.prob_user_profile[k].values())
                    user_profile[k] = keys[np.argwhere(np.random.multinomial(1, values) == 1)[0][0]]

        else:
            for k in params.prob_user_profile.keys():
                user_profile[k] = getattr(params, k)

        print(json.dumps(user_profile, indent=2))
        return user_profile

    def generate_user_agenda(self):
        params = self.params
        user_agenda = []
        print("Constructing new user agenda.")
        if self.user_profile['initiative'] == 'high':
            keys = list(params.prob_user_behaviour['inform_slot'].keys())
            values = list(params.prob_user_behaviour['inform_slot'].values())

            slot = keys[np.argwhere(np.random.multinomial(1, values) == 1)[0][0]]
            value = self.slot_values[slot]

            ts = params.construct_ts('inform', slot, value)
            cs = 'HE' if self.user_profile['conv_goal_type'] == 'i' else 'NONE'
            user_agenda.append({'ts': ts, 'cs': cs})

        user_agenda.append({'ts': params.construct_ts('bye'), 'cs': 'NONE'})
        print(json.dumps(user_agenda, indent=2))
        return user_agenda

    def get_slot_values(self):
        print("Getting new slot values.")
        params = self.params
        slot_values = {}
        for inf_slot in params.informable_slots:
            if self.user_profile[inf_slot + '_preference'] == 'single_preference':
                with open(os.path.join(params.lexicons_folder_path, inf_slot + '-list'), 'rb') as f:
                    full_list = pickle.load(f)
                slot_values[inf_slot] = random.sample(full_list, 1)[0]
        print(json.dumps(slot_values, indent=2))
        return slot_values
