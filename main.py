import os
import numpy as np
import argparse
import random
import json
import pickle
from src import config
from src import user_simulator
from src import dialog_state_tracker
from src.agent import rule_based_agent
from src.util import scenario_reader, run_and_convert_dialogs

# np.random.seed(0)
# random.seed(0)


def verify_arguments(args):
    if args.command_line_user not in [0, 1]:
        raise ValueError('%d command_line_user not supported.' % args.command_line_user)
    if args.num_dialogs_synthetic < 1:
        raise ValueError('%d num_dialogs_synthetic not supported.' % args.num_dialogs_synthetic)
    if args.num_dialogs_rl < 1:
        raise ValueError('%d num_dialogs_rl not supported.' % args.num_dialogs_rl)

    if args.conv_goal_type not in config.CONV_GOAL_TYPES:
        raise ValueError('%s conv_goal_type not supported.' % args.conv_goal_type)
    if args.initiative not in config.INITIATIVE_TYPES:
        raise ValueError('%s initiative not supported.' % args.initiative)
    if args.actor_preference not in config.SLOT_PREFERENCE_TYPES:
        raise ValueError('%s actor_preference not supported.' % args.actor_preference)
    if args.genre_preference not in config.SLOT_PREFERENCE_TYPES:
        raise ValueError('%s genre_preference not supported.' % args.genre_preference)
    if args.director_preference not in config.SLOT_PREFERENCE_TYPES:
        raise ValueError('%s director_preference not supported.' % args.director_preference)
    if args.cooperation_type not in config.COOPERATION_TYPES:
        raise ValueError('%s cooperation_type not supported.' % args.cooperation_type)

    if args.agent_type not in config.AGENT_TYPE:
        raise ValueError('%s agent_type not supported.' % args.agent_type)
    if args.agent_social_type not in config.AGENT_SOCIAL_TYPE:
        raise ValueError('%s agent_social_type not supported.' % args.agent_social_type)

    if args.generate_natural_dialogs not in [0, 1]:
        raise ValueError('%d generate_natural_dialogs not supported.' % args.generate_natural_dialogs)
    if args.generate_synthetic_data not in [0, 1]:
        raise ValueError('%d generate_synthetic_data not supported.' % args.generate_synthetic_data)
    if args.print_info not in [0, 1, 2]:
        raise ValueError('%d print_info not supported.' % args.print_info)
    if args.write_to_file not in [0, 1]:
        raise ValueError('%d write_to_file not supported.' % args.write_to_file)
    if args.control_setting not in [0, 1]:
        raise ValueError('%d control_setting not supported.' % args.control_setting)
    if args.save_dialog_data not in [0, 1]:
        raise ValueError('%d save_dialog_data not supported.' % args.save_dialog_data)


def evaluate_dialogs(dialog_list, key, k, ack=False):
    all_flows = []
    all_turns = []
    orig_k = k
    for i, dialog in enumerate(dialog_list):
        flow = []
        all_turns.append(len(list(dialog.keys())))
        for turn in dialog:
            agent_turn = dialog[turn][config.AGENT_STR]
            if key == config.CS_STR:
                if ack:
                    flow.append((agent_turn[config.AGENT_ACTION_DICT_STR][config.ACTION_STR][1], agent_turn[config.AGENT_DF_STR][key]))
                else:
                    flow.append(agent_turn[config.AGENT_DF_STR][key])
            elif key == config.TS_STR:
                flow.append(config.deconstruct_ts(agent_turn[config.AGENT_DF_STR][key])[0])
            else:
                flow.append((agent_turn[config.AGENT_ACTION_DICT_STR][config.ACTION_STR][1], config.deconstruct_ts(agent_turn[config.AGENT_DF_STR][config.TS_STR])[0],
                            agent_turn[config.AGENT_DF_STR][config.CS_STR]))
            user_turn = dialog[turn][config.USER_STR]
            if key == config.CS_STR:
                flow.append(user_turn[config.USER_DF_STR][key])
            elif key == config.TS_STR:
                flow.append(config.deconstruct_ts(user_turn[config.USER_DF_STR][key])[0])
            else:
                flow.append((config.deconstruct_ts(user_turn[config.USER_DF_STR][config.TS_STR])[0], user_turn[config.USER_DF_STR][config.CS_STR]))
        k = min(orig_k, len(flow))
        i = 0
        while i + k <= len(flow):
            all_flows.append(tuple(flow[i:i + k]))
            print(tuple(flow[i:i + k]))
            i += 1

    values = list(set(all_flows))
    keys = list(range(len(values)))
    dictionary = dict(zip(keys, values))
    print(json.dumps(dictionary, indent=2))
    print(len(set(all_flows)))
    print(len(all_flows))
    print("Average number of turns: ", sum(all_turns)/len(all_turns))
    return len(set(all_flows))/len(all_flows)


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
    parser.add_argument('--agent_task_fname', dest='agent_task_fname', type=str,
                        default='agent_task_utterances.tsv', help='Name of agent task utterances file.')
    parser.add_argument('--agent_ack_fname', dest='agent_ack_fname', type=str,
                        default='agent_ack_utterances.tsv', help='Name of agent ack utterances file.')
    parser.add_argument('--user_task_fname', dest='user_task_fname', type=str,
                        default='user_task_utterances.tsv', help='Name of user task utterances file.')
    parser.add_argument('--dialog_fname', dest='dialog_fname', type=str,
                        default='dialog_list', help='Name of user synthetic dialog data file.')

    parser.add_argument('--command_line_user', dest='command_line_user', type=int,
                        default=0, help='Whether to have a command line user simulator or not.')
    parser.add_argument('--num_dialogs_synthetic', dest='num_dialogs_synthetic', type=int,
                        default=2000, help='Number of synthetic dialogs.')
    parser.add_argument('--num_dialogs_rl', dest='num_dialogs_rl', type=int,
                        default=1, help='Number of RL dialogs.')

    parser.add_argument('--agent_type', dest='agent_type', type=str,
                        default='rule_based', help='Type of agent: rule_based or rl.')
    parser.add_argument('--agent_social_type', dest='agent_social_type', type=str,
                        default='full-social', help='Type of agent: social or unsocial (NONE CS).')
    parser.add_argument('--user_simulator_only', dest='user_simulator_only', type=int,
                        default=1, help='Only use user simulator.')

    parser.add_argument('--generate_natural_dialogs', dest='generate_natural_dialogs', type=int,
                        default=1, help='Flag denoting whether or not synthetic natural '
                                        'language dialogs need to be generated.')
    parser.add_argument('--generate_synthetic_data', dest='generate_synthetic_data', type=int,
                        default=1, help='Flag denoting whether or not synthetic data '
                                        'at dialog frame level need to be generated.')
    parser.add_argument('--print_info', dest='print_info', type=int,
                        default=1, help='Flag for printing information.')
    parser.add_argument('--write_to_file', dest='write_to_file', type=int,
                        default=0, help='Flag for writing to file.')
    parser.add_argument('--control_setting', dest='control_setting', type=int,
                        default=0, help='Free-flow data generation or control setting.')
    parser.add_argument('--save_dialog_data', dest='save_dialog_data', type=int,
                        default=1, help='Save synthetic dialog data for training SL/RL+SL agent.')

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

    args.user_sim = user_simulator.UserSimulator(args, user_sim_reasoner)
    args.state_tracker = dialog_state_tracker.StateTracker(args)
    args.agent = rule_based_agent.RuleBasedAgent(args, agent_reasoner)

    if args.generate_synthetic_data == 1:
        num_dialogs = args.num_dialogs_synthetic
        run_and_convert_dialogs.run_dialogs(args, num_dialogs)


if __name__ == "__main__":
    main()
