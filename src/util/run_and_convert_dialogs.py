import random
import csv
import pickle
import os
import json
from src import config
from src.util import nlg_db_reader, utterance_generator
from src.util import muf_simulator


def run_dialogs(args, num_dialogs):
    """
    :param args: All the parser (command line) arguments.
    :param num_dialogs: Number of dialogs to run.
    :return: A list of dialogs (semantic, NL). Each dialog is a dictionary with keys as turns and
            values as everything else: (a) State, User + Agent dialog frame, ACK key, task key.
    """
    full_id_list = []
    agent_ack_file_path = os.path.join(args.nlg_db_folder_path, args.agent_ack_fname)
    agent_ack_nlg_db = nlg_db_reader.read_nlg_db(agent_ack_file_path, config.NUM_FIELDS_NLG_AGENT)

    agent_task_file_path = os.path.join(args.nlg_db_folder_path, args.agent_task_fname)
    agent_task_nlg_db = nlg_db_reader.read_nlg_db(agent_task_file_path, config.NUM_FIELDS_NLG_AGENT)

    user_task_file_path = os.path.join(args.nlg_db_folder_path, args.user_task_fname)
    user_task_nlg_db = nlg_db_reader.read_nlg_db(user_task_file_path, config.NUM_FIELDS_NLG_USER)

    nlg_options = list(list(agent_ack_nlg_db.values())[0].keys())[:config.NUM_USABLE_NL]

    for _ in range(num_dialogs):
        file_id = str(random.randint(0, config.LARGEST_FILE_ID))
        full_id_list.append(file_id)

        args.user_sim.reset()
        state = args.state_tracker.reset()
        dialog_over = False

        agent_action_dict_list = []
        user_action_dict_list = []

        nlg_id = random.sample(nlg_options, 1)[0]
        utter_gen = utterance_generator.UtteranceGenerator(
            agent_ack_nlg_db=agent_ack_nlg_db,
            agent_task_nlg_db=agent_task_nlg_db,
            user_task_nlg_db=user_task_nlg_db,
            nlg_id=nlg_id,
            nlg_options=nlg_options
        )

        user_utterance = b'{\"messageId\":\"MSG_START_INTERACTION\",\"payload\":\"\",\"requestType\":\"\",\"sessionId\":\"\"}'
        phone_id = "0123456789abcdef"
        ip_address = "128.237.207.193"
        socket = muf_simulator.simulation(phone_id, ip_address)
        print("MUF simulator called.")

        while not dialog_over:
            agent_action = muf_simulator.exchange(socket, phone_id, user_utterance)
            state, dialog_over, full_dialog = args.state_tracker.step(agent_action=agent_action)

            user_action_dict = args.user_sim.next(state, agent_action)
            user_action_dict_list.append(user_action_dict)
            user_action = user_action_dict[config.ACTION_STR]
            user_utterance = utter_gen.process_utterance(state, utter_gen.get_user_utterance(user_action_dict))
            state, dialog_over, full_dialog = args.state_tracker.step(user_action=user_action)
