from src import config
import random


class UtteranceGenerator:

    def __init__(self, **kwargs):
        self.agent_ack_nlg_db = kwargs['agent_ack_nlg_db']
        self.agent_task_nlg_db = kwargs['agent_task_nlg_db']
        self.user_task_nlg_db = kwargs['user_task_nlg_db']
        self.nlg_id = kwargs['nlg_id']
        self.nlg_options = kwargs['nlg_options']

    def get_agent_utterance(self, agent_action_dict):
        agent_ack_key = agent_action_dict[config.ACK_STR]
        agent_task_key = agent_action_dict[config.OTHER_STR]
        agent_utterance = ''
        if agent_ack_key is not None:
            assert agent_ack_key in self.agent_ack_nlg_db
            agent_ack_utterance = self.get_utterance(self.agent_ack_nlg_db, agent_ack_key)
            agent_utterance += agent_ack_utterance
        assert agent_task_key in self.agent_task_nlg_db
        agent_task_utterance = self.get_utterance(self.agent_task_nlg_db, agent_task_key)
        agent_utterance += ' '
        agent_utterance += agent_task_utterance
        return agent_utterance

    def get_user_utterance(self, user_action_dict):
        user_task_key = user_action_dict[config.OTHER_STR]
        assert user_task_key in self.user_task_nlg_db
        user_utterance = self.get_utterance(self.user_task_nlg_db, user_task_key)
        return user_utterance

    def get_utterance(self, db, key):
        utterance = db[key][self.nlg_id]
        while utterance == '':
            self.nlg_id = random.sample(self.nlg_options, 1)[0]
            utterance = db[key][self.nlg_id]
        return utterance
