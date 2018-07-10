import os
import numpy as np
import argparse
from src import config
from src import user_simulator

np.random.seed(0)


def verify_arguments(args):
    if args.command_line_user not in [0, 1]:
        raise ValueError('%d command_line_user value not supported.' % args.command_line_user)
    if args.conv_goal_type not in ['i', 'p']:
        raise ValueError('%s conversational goal type not supported.' % args.conv_goal_type)
    if args.initiative not in ['high', 'low']:
        raise ValueError('%s conversational goal type not supported.' % args.initiative)
    if args.actor_preference not in ['no_preference', 'single_preference']:
        raise ValueError('%s conversational goal type not supported.' % args.actor_preference)
    if args.genre_preference not in ['no_preference', 'single_preference']:
        raise ValueError('%s conversational goal type not supported.' % args.genre_preference)
    if args.director_preference not in ['no_preference', 'single_preference']:
        raise ValueError('%s conversational goal type not supported.' % args.director_preference)
    if args.cooperation_type not in ['cooperative', 'uncooperative']:
        raise ValueError('%s cooperation type not supported.' % args.cooperation_type)


def prepare_user_params(args):
    args.prob_user_profile = config.get_prob_user_profile()
    args.prob_user_behaviour = config.prob_user_behaviour
    return args


def parse_arguments():
    parser = argparse.ArgumentParser(description='Argument Parser for RL-based Dialog Manager '
                                                 'for InMind.')
    parser.add_argument('--scenario_file_name', dest='scenario_file_name', type=str,
                        default='scenario.txt', help='Name of file containing InMind scenario.')
    parser.add_argument('--data_folder_name', dest='data_folder_name', type=str,
                        default='data', help='Name of data folder.')
    parser.add_argument('--command_line_user', dest='command_line_user', type=int,
                        default=0, help='Whether to have a command line user simulator or not.')
    parser.add_argument('--num_dialogs', dest='num_dialogs', type=int,
                        default=1, help='Number of dialogs.')

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
    user_sim_params = prepare_user_params(args)

    user_sim = user_simulator.UserSimulator(user_sim_params)

    for _ in range(args.num_dialogs):
        user_sim.reset()

    # data_folder_path = os.path.join(os.getcwd(), args.data_folder_name)
    # with open(os.path.join(data_folder_path, args.scenario_file_name), 'r', encoding='UTF-8') as f:
    #     print(f.read())


if __name__ == "__main__":
    main()
