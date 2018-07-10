import numpy as np
import json


class UserSimulator:
    def __init__(self, params):
        self.params = params
        self.user_profile = None

    def reset(self):
        self.user_profile = self.generate_user_profile()

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

    # @staticmethod
    # def generate_user_agenda():
    #         user_agenda = []
    #     return user_agenda

    # def next(self, agent_df):
    #     r_t = self.update_agenda(agent_action)
    #
    # return self.agenda.pop(), r_t