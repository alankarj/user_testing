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
        self.user_agenda = None

    def reset(self):
        self.user_profile = self.generate_user_profile()
        self.slot_values = self.get_slot_values()
        self.user_agenda = self.generate_user_agenda()
        return self.user_profile

    def generate_user_profile(self):
        params = self.params
        user_profile = {}
        prob_user_profile = config.get_prob_user_profile()

        if params.command_line_user == 0:
            print("Spawning new user profile.")
            for k in prob_user_profile.keys():
                if type(prob_user_profile[k]) is dict:
                    user_profile[k] = self.get_dice_roll_result(prob_user_profile[k])

        else:
            for k in prob_user_profile.keys():
                user_profile[k] = getattr(params, k)

        print(json.dumps(user_profile, indent=2))
        return user_profile

    @staticmethod
    def generate_user_agenda():
        user_agenda = []
        print("Constructing new user agenda.")
        print(json.dumps(user_agenda, indent=2))
        return user_agenda

    def get_slot_values(self):
        print("Getting new slot values.")
        params = self.params
        slot_values = {}
        for inf_slot in config.INFORMABLE_SLOTS:
            # If the user has single preference for an inform slot, sample uniformly at random from the list of slot values.
            if self.user_profile[inf_slot + config.SLOT_PREFERENCE_TYPE_STR] == config.SLOT_PREFERENCE_TYPES[0]:
                slot_values[inf_slot] = self.sample_slot_value(inf_slot)
        print(json.dumps(slot_values, indent=2))
        return slot_values

    def sample_slot_value(self, slot):
        params = self.params
        with open(os.path.join(params.lexicons_folder_path, slot + config.SLOT_LISTS_FILE_SUFFIX), 'rb') as f:
            full_list = pickle.load(f)
        return random.sample(full_list, 1)[0]

    def next(self, state, agent_action):
        """
        :param state: Dictionary of dictionaries (task_state and social_state)
        :param agent_action: 5-tuple containing ts_string_ack, ack_cs, ts_string_other, other_cs, value
        :return: user_action: 3-tuple containing ts_string, cs, value
        """
        agent_action = agent_action.split(',')
        print(agent_action)
        for aa in agent_action:
            aa = aa.strip("()")
        if agent_action[1] == 'ASN':
            agent_action[1] = 'NONE'
        if agent_action[3] == 'ASN':
            agent_action[3] = 'NONE'
        if agent_action[2] == 'request(why)':
            agent_action[2] = 'request(reason_not_like)'
        if agent_action[2] == 'request(another)':
            agent_action[2] = 'request(another_one)'
        if agent_action[2] == 'inform(plot)':
            agent_action[2] = 'inform(movie_info)'
        if agent_action[2] in ['request(genre)', 'request(actor)', 'request(director)', 'inform(movie)', 'request(reason_not_like)']:
            agent_action[3] = 'QESD'
        if agent_action[2] in ['inform(actor)', 'inform(genre)', 'inform(movie_info)', 'request(feedback)']:
            agent_action[3] = 'NONE'
        agent_action = tuple(agent_action)
        print(agent_action)
        if len(agent_action) != config.AGENT_ACTION_DIM:
            raise ValueError("Size of agent_action: %d does not match expected size: %d."
                             % (len(agent_action), config.AGENT_ACTION_DIM))

        user_ts_string, value = self.task_reasoner(state, agent_action)
        cs_list = self.reasoner[agent_action[config.TS_STR_INDEX_AGENT:config.SLOT_VALUE_INDEX_AGENT]][user_ts_string]
        cs = self.social_reasoner(cs_list)
        ts_key = (agent_action[config.TS_STR_INDEX_AGENT], user_ts_string, cs)
        return {config.ACTION_STR: (user_ts_string, cs, value), config.OTHER_STR: ts_key}

    def task_reasoner(self, state, agent_action):
        """
        :param state: Dictionary of dictionaries (task_state and social_state)
        :param agent_action: 5-tuple containing ts_string_ack, ack_cs, ts_string_other, other_cs, value
        :return: 2-tuple containing user_ts_string and user_value
        """
        task_state = state[config.TASK_STATE_STR]
        agent_action_key = agent_action[config.TS_STR_INDEX_AGENT:config.SLOT_VALUE_INDEX_AGENT]
        print(agent_action_key)
        assert agent_action_key in self.reasoner
        ts_list = list(self.reasoner[agent_action_key].keys())

        agent_ts_string = agent_action[config.TS_STR_INDEX_AGENT]
        agent_intent, agent_slot = config.parse_ts_string(agent_ts_string)

        user_value = ''

        if agent_ts_string == config.AGENT_TS_STRINGS[0]:
            if (self.user_profile[config.COOPERATION_TYPE_STR] == config.COOPERATION_TYPES[0]) and \
                    (self.user_profile[config.INITIATIVE_TYPE_STR] == config.INITIATIVE_TYPES[0]) and \
                        (self.slot_values != {}):
                # High initiative user.
                dictionary = config.PROB_USER_BEHAVIOUR[config.INFORM_STR + '_' + config.SLOT_STR]
                valid_slot_found = False
                slot = None
                value = None
                while not valid_slot_found:
                    slot = self.get_dice_roll_result(dictionary)
                    if slot in self.slot_values:
                        valid_slot_found = True
                        value = self.slot_values[slot]
                user_ts_string, user_value = config.deconstruct_ts(config.construct_ts(config.INFORM_STR, slot, value))

            else:
                user_ts_string = self.get_cooperation_response(ts_list)

        elif agent_ts_string == config.AGENT_TS_STRINGS[1]:
            user_ts_string = self.get_cooperation_response(ts_list)

        elif (agent_intent == config.AGENT_TS_STRINGS[2]) and (agent_slot in config.INFORMABLE_SLOTS):
            if self.user_profile[agent_slot + config.SLOT_PREFERENCE_TYPE_STR] == config.SLOT_PREFERENCE_TYPES[0]:
                # If the user has a preferred genre/actor/director.
                user_ts_string = ts_list[0]
                user_value = self.slot_values[agent_slot]
            else:
                user_ts_string = ts_list[1]

        elif agent_ts_string == config.AGENT_TS_STRINGS[3]:
            if task_state[config.RECOS_STR] < config.MAX_RECOS:
                if self.user_profile[config.INITIATIVE_TYPE_STR] == config.INITIATIVE_TYPES[1]:
                    # Say yes/no if number of recos made is less than max_recos and if initiative type is low.
                    user_ts_string = self.get_movie_response(ts_list)
                else:
                    inf_req_str = self.get_dice_roll_result(config.PROB_USER_BEHAVIOUR[config.INFORM_REQUEST_MOVIE_STR])
                    if inf_req_str == config.INFORM_REQUEST_MOVIE_TYPES[0]:
                        slot = self.get_dice_roll_result(config.PROB_USER_BEHAVIOUR[config.REQUEST_STR + '_' + config.SLOT_STR])
                    else:
                        slot = self.get_dice_roll_result(config.PROB_USER_BEHAVIOUR[config.INFORM_STR + '_' + config.SLOT_STR])
                    user_ts_string = inf_req_str + '(' + slot + ')'
                    if inf_req_str == config.INFORM_STR and slot in config.INFORMABLE_SLOTS:
                        user_value = self.sample_slot_value(slot)

            elif task_state[config.RECOS_STR] == config.MAX_RECOS:
                # Say yes/no if number of recos made equals max_recos.
                user_ts_string = self.get_movie_response(ts_list)

            else:
                # Say no if number of recos made exceeds max_recos.
                user_ts_string = ts_list[1]

        elif agent_ts_string in [config.AGENT_TS_STRINGS[4], config.AGENT_TS_STRINGS[5]]:
            if task_state[config.RECOS_STR] < config.MAX_RECOS:
                # Say yes/no if number of recos made is less than max_recos.
                user_ts_string = self.get_movie_response(ts_list)
            else:
                # Say no if number of recos made equals max_recos.
                user_ts_string = ts_list[1]

        else:
            # There's just a single option now.
            user_ts_string = ts_list[0]

        assert type(user_ts_string) == str
        assert type(user_value) == str
        return user_ts_string, user_value

    def social_reasoner(self, cs_list):
        params = self.params
        if len(cs_list) == 1 or self.user_profile[config.CONV_GOAL_TYPE_STR] != config.CONV_GOAL_TYPES[0]:
            # P-type user!
            cs = cs_list[0]
        else:
            cs = random.sample(cs_list[1:], 1)[0]
        return cs

    def get_cooperation_response(self, ts_list):
        if self.user_profile[config.COOPERATION_TYPE_STR] == config.COOPERATION_TYPES[0]:
            user_ts_string = ts_list[0]
        else:
            user_ts_string = ts_list[1]
        return user_ts_string

    @staticmethod
    def get_movie_response(ts_list):
        """
        :param ts_list: List of ts_strings (agent)
        :return: us_ts_string (user)
        """
        if random.random() < config.PROB_USER_BEHAVIOUR[config.ACCEPTANCE_STR]:
            user_ts_string = ts_list[0]
        else:
            user_ts_string = ts_list[1]
        return user_ts_string

    @staticmethod
    def get_dice_roll_result(dictionary):
        """
        :param dictionary: dict containing string keys and probability values
        :return: string (result of a dice roll with probability values given in dictionary)
        """
        if type(dictionary) is not dict:
            raise ValueError("Input should be a dictionary.")
        keys = list(dictionary.keys())
        values = list(dictionary.values())
        # Pick a value based on multinomial distribution.
        selected_string = keys[np.argwhere(np.random.multinomial(1, values) == 1)[0][0]]
        assert type(selected_string) == str
        return selected_string
