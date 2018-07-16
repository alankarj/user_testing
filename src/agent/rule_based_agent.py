import random
from src import config


class RuleBasedAgent:
    def __init__(self, params, agent_reasoner):
        self.params = params
        self.reasoner = agent_reasoner

    def next(self, state):
        task_state = state[config.TASK_STATE_STR]
        agent_ts_string = config.deconstruct_ts(task_state[config.AGENT_DF_STR][config.TS_STR])[0]

        user_df = task_state[config.USER_DF_STR]
        user_ts_string = config.deconstruct_ts(user_df[config.TS_STR])[0]
        user_cs = user_df[config.CS_STR]

        key = (agent_ts_string, user_ts_string, user_cs)
        correct_ts_string_found = False

        agent_ts_string_ack, agent_cs_ack = '', ''
        agent_ts_string_other, agent_cs_other = '', ''
        ack_key, ts_key = '', ''

        if task_state[config.TURN_STR] > 0:
            if self.params.control_setting == 0 or (self.params.agent_social_type != config.AGENT_SOCIAL_TYPE[0]):
                agent_ts_string_ack, agent_cs_ack, ack_key = self.reasoner_helper(self.reasoner[config.ACK_STR], key)

        while not correct_ts_string_found:
            agent_ts_string_other, agent_cs_other, ts_key = self.reasoner_helper(self.reasoner[config.OTHER_STR], key, ack_cs=agent_cs_ack)

            for s in config.INFORMABLE_SLOTS:
                if agent_ts_string_other == config.REQUEST_STR + '(' + s + ')':
                    if task_state[s] != '':
                        correct_ts_string_found = False
                        key = (agent_ts_string_other, config.INFORM_STR + '(' + s + ')', '')
                        break
                else:
                    correct_ts_string_found = True

        agent_intent, slot = config.parse_ts_string(agent_ts_string_other)
        value = ''
        if agent_intent == config.INFORM_STR:
            if slot == config.MOVIE_STR:
                user_slots_dict = {}
                for s in config.INFORMABLE_SLOTS:
                    user_slots_dict[s] = task_state[s]
                value = config.interface_with_recommendation_system(user_slots_dict)
            elif slot in config.REQUESTABLE_SLOTS + config.REQUESTABLE_SLOTS_PSEUDO:
                value = config.interface_with_omdb(slot)

        assert agent_ts_string_other != ''
        assert agent_cs_other != ''

        ack_key_nlg = None
        if agent_ts_string_ack != '':
            ack_key_nlg = (*ack_key, agent_ts_string_ack, agent_cs_ack)
        if agent_ts_string_other == config.AGENT_TS_STRINGS[3]:
            ts_key = ('', '', '')
        ts_key_nlg = (*ts_key, agent_ts_string_other, agent_cs_other)

        return {config.ACTION_STR: (agent_ts_string_ack, agent_cs_ack, agent_ts_string_other, agent_cs_other, value),
                config.ACK_STR: ack_key_nlg,
                config.OTHER_STR: ts_key_nlg}

    def reasoner_helper(self, dictionary, key, ack_cs=None):
        """
        :param dictionary: ACK/TASK Reasoner
        :param key: Triple of (prev_agent_ts_string, user_ts_string, user_cs)
        :param ack_cs: ACK CS
        :return: Tuple of (agent_ts_string, agent_cs, return_key)
        """
        if len(key) != config.USER_ACTION_DIM:
            raise ValueError("Size of key: %d does not match expected size: %d." % (len(key), config.USER_ACTION_DIM))
        alt_key = (key[0], key[1], '')
        return_key = key

        if (ack_cs is not None) and (alt_key in config.get_agent_loop_keys()):
            ts_string = config.INFORM_STR + '(' + config.MOVIE_STR + ')'
            cs_list = config.INFORM_MOVIES_CS_LIST
            return_key = alt_key
        else:
            if key not in dictionary:
                key = alt_key
                return_key = alt_key
            if key in dictionary:
                ts_string = list(dictionary[key].keys())[0]
                cs_list = list(dictionary[key].values())[0]
            else:
                return '', '', ''
        cs = self.social_reasoner(cs_list, ack_cs)
        return ts_string, cs, return_key

    def social_reasoner(self, cs_list, ack_cs=None):
        params = self.params
        cs = ack_cs
        if params.control_setting == 0:
            cs = random.sample(cs_list, 1)[0]

        else:
            if params.agent_social_type == config.AGENT_SOCIAL_TYPE[2]:
                while cs == ack_cs:
                    if len(cs_list) > 1:
                        cs = random.sample(cs_list[1:], 1)[0]
                    else:
                        cs = cs_list[0]
            else:
                cs = cs_list[0]
        assert cs != ''
        return cs
