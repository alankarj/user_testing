import random
import csv
import pickle
import os
import json
from src import config
from src.util import nlg_db_reader, utterance_generator


def run_dialogs(args, num_dialogs):
    """
    :param args: All the parser (command line) arguments.
    :param num_dialogs: Number of dialogs to run.
    :return: A list of dialogs (semantic, NL). Each dialog is a dictionary with keys as turns and
            values as everything else: (a) State, User + Agent dialog frame, ACK key, task key.
    """
    dialog_list = []
    nl_dialog_list = None
    full_id_list = []

    for _ in range(num_dialogs):
        file_id = str(random.randint(0, config.LARGEST_FILE_ID))
        full_id_list.append(file_id)

        user_profile = args.user_sim.reset()
        state = args.state_tracker.reset()
        dialog_over = False

        agent_action_dict_list = []
        user_action_dict_list = []

        turn = 0
        while not dialog_over:
            agent_action_dict = args.agent.next(state)
            agent_action_dict_list.append(agent_action_dict)
            agent_action = agent_action_dict[config.ACTION_STR]
            state, dialog_over, full_dialog = args.state_tracker.step(agent_action=agent_action)

            user_action_dict = args.user_sim.next(state, agent_action)
            user_action_dict_list.append(user_action_dict)
            user_action = user_action_dict[config.ACTION_STR]
            state, dialog_over, full_dialog = args.state_tracker.step(user_action=user_action)

            turn += 1

            if args.print_info == 2:
                print("Agent action: ", agent_action)
                print("User action: ", user_action)
                print("State: ", json.dumps(state, indent=2))

        for i in range(turn):
            full_dialog[i][config.AGENT_STR][config.AGENT_ACTION_DICT_STR] = agent_action_dict_list[i]
            full_dialog[i][config.USER_STR][config.USER_ACTION_DICT_STR] = user_action_dict_list[i]

        dialog_list.append(full_dialog)
        if args.write_to_file:
            with open(os.path.join(args.synthetic_dialogs_folder_path, file_id + '_full_dialog.pkl'), 'wb') as fp:
                pickle.dump(full_dialog, fp)
            with open(os.path.join(args.synthetic_dialogs_folder_path, file_id + '_user_profile.pkl'), 'wb') as fp:
                pickle.dump(user_profile, fp)

    if args.generate_natural_dialogs == 1:
        nl_dialog_list = convert_to_nl(args, dialog_list, full_id_list)

    return dialog_list, nl_dialog_list


def convert_to_nl(args, dialog_list, full_id_list):
    """
    :param args: All the parser (command line) arguments.
    :param dialog_list: A list of dialogs at dialog frame level.
    :param full_id_list: A list containing the synthetic dialog IDs.
    :return: A list of dialogs are natural language level.
    """
    agent_ack_file_path = os.path.join(args.nlg_db_folder_path, args.agent_ack_fname)
    agent_ack_nlg_db = nlg_db_reader.read_nlg_db(agent_ack_file_path, config.NUM_FIELDS_NLG_AGENT)

    agent_task_file_path = os.path.join(args.nlg_db_folder_path, args.agent_task_fname)
    agent_task_nlg_db = nlg_db_reader.read_nlg_db(agent_task_file_path, config.NUM_FIELDS_NLG_AGENT)

    user_task_file_path = os.path.join(args.nlg_db_folder_path, args.user_task_fname)
    user_task_nlg_db = nlg_db_reader.read_nlg_db(user_task_file_path, config.NUM_FIELDS_NLG_USER)

    nlg_options = list(list(agent_ack_nlg_db.values())[0].keys())[:config.NUM_USABLE_NL]

    nl_dialogs = []
    for i, dialog in enumerate(dialog_list):
        file_id = full_id_list[i]
        nlg_id = random.sample(nlg_options, 1)[0]
        utter_gen = utterance_generator.UtteranceGenerator(
            agent_ack_nlg_db=agent_ack_nlg_db,
            agent_task_nlg_db=agent_task_nlg_db,
            user_task_nlg_db=user_task_nlg_db,
            nlg_id=nlg_id,
            nlg_options=nlg_options
        )

        dialog_str = ''

        for turn in dialog:
            agent_turn = dialog[turn][config.AGENT_STR]
            agent_action_dict = agent_turn[config.AGENT_ACTION_DICT_STR]
            agent_state = agent_turn[config.NEXT_STATE_STR]
            agent_utterance = utter_gen.process_utterance(agent_state, utter_gen.get_agent_utterance(agent_action_dict))
            dialog_str += config.AGENT_STR + ": " + agent_utterance + "\n"

            user_turn = dialog[turn][config.USER_STR]
            user_action_dict = user_turn[config.USER_ACTION_DICT_STR]
            user_state = user_turn[config.NEXT_STATE_STR]
            user_utterance = utter_gen.process_utterance(user_state, utter_gen.get_user_utterance(user_action_dict))
            dialog_str += config.USER_STR + ": " + user_utterance + "\n"

        nl_dialogs.append(dialog_str)

        if args.print_info == 2:
            print("Dialog ID: %d", file_id)
            print(dialog_str)

        if args.write_to_file == 1:
            with open(os.path.join(args.synthetic_dialogs_folder_path, file_id + '.txt'), 'w', encoding='UTF-8') as f:
                f.write(dialog_str)
            with open(os.path.join(args.synthetic_dialogs_folder_path, 'full_id_list' + '.csv'), 'w') as f:
                wr = csv.writer(f, quoting=csv.QUOTE_ALL)
                wr.writerow(full_id_list)
    return nl_dialogs
