import os
import numpy as np
import argparse
import random
import json
import csv
import pickle
from src import config
from src import user_simulator
from src import dialog_state_tracker
from src.agent import rule_based_agent
from src.util import scenario_reader, nlg_db_reader, utterance_generator

np.random.seed(0)
random.seed(0)


def verify_arguments(args):
    if args.command_line_user not in [0, 1]:
        raise ValueError('%d command_line_user value not supported.' % args.command_line_user)
    if args.conv_goal_type not in config.CONV_GOAL_TYPES:
        raise ValueError('%s conversational goal type not supported.' % args.conv_goal_type)
    if args.initiative not in config.INITIATIVE_TYPES:
        raise ValueError('%s conversational goal type not supported.' % args.initiative)
    if args.actor_preference not in config.SLOT_PREFERENCE_TYPES:
        raise ValueError('%s conversational goal type not supported.' % args.actor_preference)
    if args.genre_preference not in config.SLOT_PREFERENCE_TYPES:
        raise ValueError('%s conversational goal type not supported.' % args.genre_preference)
    if args.director_preference not in config.SLOT_PREFERENCE_TYPES:
        raise ValueError('%s conversational goal type not supported.' % args.director_preference)
    if args.cooperation_type not in config.COOPERATION_TYPES:
        raise ValueError('%s cooperation type not supported.' % args.cooperation_type)
    if args.agent_type not in config.AGENT_TYPE:
        raise ValueError('%s agent type not supported.' % args.agent_type)
    if args.agent_social_type not in config.AGENT_SOCIAL_TYPE:
        raise ValueError('%s agent social type not supported.' % args.agent_social_type)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Argument Parser for RL-based Dialog Manager '
                                                 'for InMind.')
    parser.add_argument('--scenario_file_name', dest='scenario_file_name', type=str,
                        default='scenario.tsv', help='Name of file containing InMind scenario.')
    parser.add_argument('--data_folder_name', dest='data_folder_name', type=str,
                        default='data', help='Name of data folder.')
    parser.add_argument('--lexicons_folder_name', dest='lexicons_folder_name', type=str,
                        default='lexicons', help='Name of lexicons folder (inside data folder).')
    parser.add_argument('--nlg_db_folder_name', dest='nlg_db_folder_name', type=str,
                        default='nlg_db', help='Name of nlg_db folder (inside data folder).')
    parser.add_argument('--synthetic_dialogs_folder_name', dest='synthetic_dialogs_folder_name', type=str,
                        default='synthetic_dialogs', help='Name of synthetic dialogs folder (inside data folder).')
    parser.add_argument('--lexicon_files_suffix', dest='lexicon_files_suffix', type=str,
                        default='2id.lexicon', help='Suffix for lexicon files.')
    parser.add_argument('--command_line_user', dest='command_line_user', type=int,
                        default=0, help='Whether to have a command line user simulator or not.')
    parser.add_argument('--num_dialogs', dest='num_dialogs', type=int,
                        default=1, help='Number of dialogs.')
    parser.add_argument('--agent_type', dest='agent_type', type=str,
                        default='rule_based', help='Type of agent: rule_based or rl.')
    parser.add_argument('--agent_social_type', dest='agent_social_type', type=str,
                        default='unsocial', help='Type of agent: social or unsocial (NONE CS).')
    parser.add_argument('--agent_task_fname', dest='agent_task_fname', type=str,
                        default='agent_task_utterances.tsv', help='Name of agent task utterances file.')
    parser.add_argument('--agent_ack_fname', dest='agent_ack_fname', type=str,
                        default='agent_ack_utterances.tsv', help='Name of agent ack utterances file.')
    parser.add_argument('--user_task_fname', dest='user_task_fname', type=str,
                        default='user_task_utterances.tsv', help='Name of user task utterances file.')

    # The following arguments determine the user profile for command line interaction.
    parser.add_argument('--conv_goal_type', dest='conv_goal_type', type=str,
                        default='i', help='Conversational goal type of the user.')
    parser.add_argument('--initiative', dest='initiative', type=str,
                        default='high', help='Initiative level of the user.')
    parser.add_argument('--actor_preference', dest='actor_preference', type=str,
                        default='single_preference', help='User preference for actor.')
    parser.add_argument('--director_preference', dest='director_preference', type=str,
                        default='no_preference', help='User preference for director.')
    parser.add_argument('--genre_preference', dest='genre_preference', type=str,
                        default='single_preference', help='User preference for genre.')
    parser.add_argument('--cooperation_type', dest='cooperation_type', type=str,
                        default='cooperative', help='Is the user cooperative or not?')

    return parser.parse_args()


def main():
    args = parse_arguments()
    verify_arguments(args)

    args.data_folder_path = os.path.join(os.getcwd(), args.data_folder_name)
    args.lexicons_folder_path = os.path.join(args.data_folder_path, args.lexicons_folder_name)
    args.nlg_db_folder_path = os.path.join(args.data_folder_path, args.nlg_db_folder_name)
    args.synthetic_dialogs_folder_path = os.path.join(args.data_folder_path, args.synthetic_dialogs_folder_name)

    scenario_file_path = os.path.join(args.data_folder_path, args.scenario_file_name)
    agent_reasoner = scenario_reader.get_agent_scenario(scenario_file_path)
    user_sim_reasoner = scenario_reader.get_user_sim_scenario(scenario_file_path)

    agent_ack_nlg_db = nlg_db_reader.read_nlg_db(
        os.path.join(args.nlg_db_folder_path, args.agent_ack_fname), config.NUM_FIELDS_NLG_AGENT)
    agent_task_nlg_db = nlg_db_reader.read_nlg_db(
        os.path.join(args.nlg_db_folder_path, args.agent_task_fname), config.NUM_FIELDS_NLG_AGENT)
    user_task_nlg_db = nlg_db_reader.read_nlg_db(
        os.path.join(args.nlg_db_folder_path, args.user_task_fname), config.NUM_FIELDS_NLG_USER)

    user_sim = user_simulator.UserSimulator(args, user_sim_reasoner)
    state_tracker = dialog_state_tracker.StateTracker(args)
    agent = rule_based_agent.RuleBasedAgent(args, agent_reasoner)

    nlg_options = list(list(agent_ack_nlg_db.values())[0].keys())[:5]
    full_id_list = []

    for _ in range(args.num_dialogs):
        nlg_id = random.sample(nlg_options, 1)[0]
        user_sim.reset()
        state = state_tracker.reset()
        dialog_over = False

        utter_gen = utterance_generator.UtteranceGenerator(
            agent_ack_nlg_db=agent_ack_nlg_db,
            agent_task_nlg_db=agent_task_nlg_db,
            user_task_nlg_db=user_task_nlg_db,
            nlg_id=nlg_id,
            nlg_options=nlg_options
        )

        file_id = str(random.randint(0, 100000))
        full_id_list.append(file_id)
        f = open(os.path.join(args.synthetic_dialogs_folder_path, file_id + '.txt'), 'w', encoding='UTF-8')

        while not dialog_over:
            agent_action_dict = agent.next(state)
            agent_action = agent_action_dict[config.ACTION_STR]
            agent_utterance = utter_gen.get_agent_utterance(agent_action_dict)
            state, dialog_over, full_dialog = state_tracker.step(agent_action=agent_action)

            user_action_dict = user_sim.next(state, agent_action)
            user_action = user_action_dict[config.ACTION_STR]
            user_utterance = utter_gen.get_user_utterance(user_action_dict)
            state, dialog_over, full_dialog = state_tracker.step(user_action=user_action)

            # print("Agent action: ", agent_action)
            # print("Agent utterance: ", agent_utterance)
            # print("User action: ", user_action)
            # print("User utterance: ", user_utterance)
            # print("State: ", json.dumps(state, indent=2))

            if dialog_over:
                with open(os.path.join(args.synthetic_dialogs_folder_path, file_id + '.pkl'), 'wb') as fp:
                    pickle.dump(full_dialog, fp)
                # print("Full dialog: ", json.dumps(full_dialog, indent=2))

            f.write(config.AGENT_STR + ": " + agent_utterance + "\n")
            f.write(config.USER_STR + ": " + user_utterance + "\n")
        f.close()
    print(full_id_list)
    with open(os.path.join(args.synthetic_dialogs_folder_path, 'full_id_list' + '.csv'), 'w') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerow(full_id_list)


if __name__ == "__main__":
    main()
