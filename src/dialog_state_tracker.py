from src import config


class StateTracker:
    def __init__(self, params):
        self.params = params
        self.state = {config.TASK_STATE_STR: None, config.SOCIAL_STATE_STR: None}
        self.dialog_over = None
        self.full_dialog = {}

    def reset(self):
        task_state = {}
        for inf_slot in config.INFORMABLE_SLOTS + config.INFORMABLE_SLOTS_PSEUDO:
            task_state[inf_slot] = ''
        for req_slot in config.REQUESTABLE_SLOTS + config.REQUESTABLE_SLOTS_PSEUDO:
            task_state[config.REQUEST_STR + '_' + req_slot] = ''
        task_state[config.TURN_STR] = 0
        task_state[config.RECOS_STR] = 0
        task_state[config.PREV_AGENT_DF_STR] = config.BLANK_DF
        task_state[config.PREV_USER_DF_STR] = config.BLANK_DF
        task_state[config.AGENT_DF_STR] = config.BLANK_DF
        task_state[config.USER_DF_STR] = config.BLANK_DF
        task_state[config.AGENT_ACK_DF_STR] = config.BLANK_DF
        self.state[config.TASK_STATE_STR] = task_state
        self.dialog_over = False
        return self.state

    def step(self, user_action=None, agent_action=None):
        """
        Updates the state based on input user action and agent action and returns it.
        :param user_action: 3-tuple containing string user_ts_string (for example: 'greeting' or 'inform(genre'),
                            string user_cs ('NONE', 'HE', etc.) and string slot_value
        :param agent_action: 5-tuple containing string agent_ts_string_ack, string agent_cs_ack, agent_ts_string_other
                            (for example: 'greeting' or 'request(genre'), string agent_cs_other ('NONE', 'HE', etc.)
                            and string slot_value
        :return: state: updated state dictionary
        """
        task_state = self.state[config.TASK_STATE_STR]

        if user_action is not None:
            intent, slot = config.parse_ts_string(user_action[config.TS_STR_INDEX_USER])
            user_df = {
                config.TS_STR: config.construct_ts(
                    intent, slot, user_action[config.SLOT_VALUE_INDEX_USER]),
                config.CS_STR: user_action[config.CS_STR_INDEX_USER]
            }

            for inf_slot in config.INFORMABLE_SLOTS:
                if slot == inf_slot:
                    task_state[inf_slot] = user_action[config.SLOT_VALUE_INDEX_USER]

            for i, inf_slot in enumerate(config.INFORMABLE_SLOTS_PSEUDO):
                if slot == inf_slot:
                    task_state[inf_slot] = config.INFORMABLE_SLOTS_PSEUDO_PLACEHOLDERS[i]

            if intent == config.REQUEST_STR:
                # Update the requestable slots to reflect that the user requested for these slots.
                for req_slot in config.REQUESTABLE_SLOTS + config.REQUESTABLE_SLOTS_PSEUDO:
                    if slot == req_slot:
                        task_state[config.REQUEST_STR + '_' + req_slot] = config.REQUEST_PLACEHOLDER

            task_state[config.PREV_USER_DF_STR] = task_state[config.USER_DF_STR]
            task_state[config.USER_DF_STR] = user_df

            if user_action[config.TS_STR_INDEX_USER] == config.NON_REQINF_USER_TS[-1]:
                self.dialog_over = True

        if agent_action is not None:
            intent, slot = config.parse_ts_string(agent_action[config.TS_STR_INDEX_AGENT])
            agent_df = {
                config.TS_STR: config.construct_ts(
                    intent, slot, agent_action[config.SLOT_VALUE_INDEX_AGENT]),
                config.CS_STR: agent_action[config.CS_STR_INDEX_AGENT]
            }

            ack_intent, ack_slot = config.parse_ts_string(agent_action[config.TS_STR_INDEX_USER])
            agent_ack_df = {
                config.TS_STR: config.construct_ts(
                    ack_intent, ack_slot, ''),
                config.CS_STR: agent_action[config.CS_STR_INDEX_USER]
            }

            # Update the requestable slots to reflect that the user requested for these slots.
            for req_slot in config.REQUESTABLE_SLOTS + config.REQUESTABLE_SLOTS_PSEUDO:
                if slot == req_slot:
                    task_state[config.REQUEST_STR + '_' + req_slot] = agent_action[config.SLOT_VALUE_INDEX_AGENT]

            # Default slot value is no_preference (this doesn't change if user says negate)
            for inf_slot in config.INFORMABLE_SLOTS:
                if slot == inf_slot:
                    task_state[inf_slot] = config.SLOT_PREFERENCE_TYPES[1]

            if agent_action[config.TS_STR_INDEX_AGENT] == config.AGENT_TS_STRINGS[3]:
                # inform(movie)
                task_state[config.RECOS_STR] += 1

            task_state[config.PREV_AGENT_DF_STR] = task_state[config.AGENT_DF_STR]
            task_state[config.AGENT_DF_STR] = agent_df
            task_state[config.AGENT_ACK_DF_STR] = agent_ack_df

        task_state[config.TURN_STR] += 0.5
        self.state[config.TASK_STATE_STR] = task_state

        if task_state[config.TURN_STR].is_integer():
            self.full_dialog[int(task_state[config.TURN_STR])] = {
                config.AGENT_STR: {
                    config.ACK_STR: task_state[config.AGENT_ACK_DF_STR],
                    config.OTHER_STR: task_state[config.AGENT_DF_STR]
                },
                config.USER_STR: task_state[config.USER_DF_STR]
            }

        return self.state, self.dialog_over, self.full_dialog
