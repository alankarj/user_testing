import os
import numpy as np
import argparse
import random
import json
from src import config
from src import user_simulator
from src import dialog_state_tracker
from src.agent import rule_based_agent

np.random.seed(0)
random.seed(0)

CONTEXT_KEY = 0  # Key to uniquely determine context for affirm/negate
AGENT_KEY = 1  # Column ID of the key for programmed agent reasoner (prev_user_ts)
USER_KEY = 3  # Column ID of the key for user simulator reasoner (agent_ts)
NUM_FIELDS_KEYS = 2  # Number of fields for agent/user simulator reasoner keys (ts, cs)

FILE_DELIMITER = '\t'  # TSV files
OPTIONS_DELIMITER = ','  # Delimiter used for different ts/cs options


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

    data_folder_path = os.path.join(os.getcwd(), args.data_folder_name)
    with open(os.path.join(data_folder_path, args.scenario_file_name), 'r', encoding='UTF-8') as f:
        all_lines = f.readlines()

        agent_reasoner = {}
        pass
        agent_reasoner[config.ACK_STR] = {}
        agent_reasoner[config.OTHER_STR] = {}
        user_simulator_reasoner = {}

        for i, line in enumerate(all_lines):
            line = line.rstrip('\n').rstrip(FILE_DELIMITER).split(FILE_DELIMITER)

            if i != 0:
                # Construct agent reasoner.
                task_strategies = line[AGENT_KEY].split(OPTIONS_DELIMITER)
                conv_strategies = line[AGENT_KEY + NUM_FIELDS_KEYS - 1].split(OPTIONS_DELIMITER)

                for ts in task_strategies:
                    ts = ts.strip(' ""')
                    for cs in conv_strategies:
                        cs = cs.strip(' ""')

                        context = line[CONTEXT_KEY].strip(' ""')
                        pre_condition_key = (context, ts, cs)

                        post_condition_key = line[AGENT_KEY + NUM_FIELDS_KEYS]
                        if post_condition_key == config.ACK_STR:
                            reasoner_key = config.ACK_STR
                        else:
                            reasoner_key = config.OTHER_STR

                        if pre_condition_key not in agent_reasoner[reasoner_key]:
                            agent_reasoner[reasoner_key][pre_condition_key] = {}

                        if post_condition_key not in agent_reasoner[reasoner_key][pre_condition_key]:
                            agent_reasoner[reasoner_key][pre_condition_key][post_condition_key] = []

                        agent_conv_strategies = line[AGENT_KEY + 2 * NUM_FIELDS_KEYS - 1].split(OPTIONS_DELIMITER)
                        for acs in agent_conv_strategies:
                            agent_reasoner[reasoner_key][pre_condition_key][post_condition_key].append(acs.strip(' ""'))

                # Construct user reasoner.
                conv_strategies = line[USER_KEY + NUM_FIELDS_KEYS - 1].split(OPTIONS_DELIMITER)
                ts = line[USER_KEY].strip(' ""')
                if ts != config.ACK_STR:
                    for cs in conv_strategies:
                        cs = cs.strip(' ""')

                        pre_condition_key = (ts, cs)

                        if pre_condition_key not in user_simulator_reasoner:
                            user_simulator_reasoner[pre_condition_key] = {}

                        for j in range(USER_KEY + NUM_FIELDS_KEYS, len(line), NUM_FIELDS_KEYS):
                            post_condition_key = line[j].strip(' ""')
                            if post_condition_key not in user_simulator_reasoner[pre_condition_key]:
                                user_simulator_reasoner[pre_condition_key][post_condition_key] = []

                            user_conv_strategies = line[j+1].split(OPTIONS_DELIMITER)
                            for ucs in user_conv_strategies:
                                ucs = ucs.strip(' ""')
                                user_simulator_reasoner[pre_condition_key][post_condition_key].append(ucs)

    user_sim = user_simulator.UserSimulator(args, user_simulator_reasoner)
    state_tracker = dialog_state_tracker.StateTracker(args)
    agent = rule_based_agent.RuleBasedAgent(args, agent_reasoner)

    print(agent_reasoner[config.ACK_STR])
    print()
    print(agent_reasoner[config.OTHER_STR])

    # print(user_simulator_reasoner)

    for _ in range(args.num_dialogs):
        user_sim.reset()
        state = state_tracker.reset()
        dialog_over = False
        while not dialog_over:
            agent_action = agent.next(state)
            print("Agent action: ", agent_action)
            state, dialog_over, full_dialog = state_tracker.step(agent_action=agent_action)
            user_action = user_sim.next(state, agent_action)
            print("User action: ", user_action)
            state, dialog_over, full_dialog = state_tracker.step(user_action=user_action)
            print("State: ", json.dumps(state, indent=2))
            if dialog_over:
                print("Full dialog: ", json.dumps(full_dialog, indent=2))


if __name__ == "__main__":
    main()
