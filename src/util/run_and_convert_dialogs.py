import random
import os
from src import config
from src.util import nlg_db_reader, utterance_generator
from src.util import muf_simulator

DEFAULT_USER_UTTERANCE = '{\"messageId\":\"MSG_START_INTERACTION\",\"payload\":\"\",\"requestType\":\"\",\"sessionId\":\"\"}'
DEFAULT_PHONE_ID = "0123456789abcdef"
# DEFAULT_IP_ADDRESS = "128.237.207.193"
DEFAULT_IP_ADDRESS = "127.0.0.1"


def run_dialogs(args, num_dialogs):
    # SURF client
    import src.util.surf.SURFClient as SURFClient
    import threading
    SURFClient.subscribe("MSG_NLG")
    t = threading.Thread(target=SURFClient.clientThread)
    t.start()

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
        args.state_tracker.reset()
        dialog_over = False

        nlg_id = random.sample(nlg_options, 1)[0]
        utter_gen = utterance_generator.UtteranceGenerator(
            agent_ack_nlg_db=agent_ack_nlg_db,
            agent_task_nlg_db=agent_task_nlg_db,
            user_task_nlg_db=user_task_nlg_db,
            nlg_id=nlg_id,
            nlg_options=nlg_options
        )

        user_utterance = DEFAULT_USER_UTTERANCE
        phone_id = DEFAULT_PHONE_ID
        ip_address = DEFAULT_IP_ADDRESS
        socket = muf_simulator.simulation(phone_id, ip_address)

        counter = 0
        while not dialog_over:
            if counter == 0:
                start = 1
            else:
                start = 0

            agent_action, utt = muf_simulator.exchange(socket, phone_id, user_utterance, start, send_to_surf=False)
            agent_action = parse_agent_action(agent_action)
            print("AGENT: ", utt)
            state, dialog_over, full_dialog = args.state_tracker.step(agent_action=agent_action)

            user_action_dict = args.user_sim.next(state, agent_action)
            user_action = user_action_dict[config.ACTION_STR]
            state, dialog_over, full_dialog = args.state_tracker.step(user_action=user_action)
            user_utterance = utter_gen.process_utterance(state, utter_gen.get_user_utterance(user_action_dict))
            print("USER: ", user_utterance)
            counter += 1


def parse_agent_action(agent_action):
    """
    :param agent_action: String agent_action
    :return: 5-tuple agent_action
    """
    agent_action = agent_action.split(',')
    if len(agent_action) != config.AGENT_ACTION_DIM:
        raise ValueError("Size of agent_action: %d does not match expected size: %d."
                         % (len(agent_action), config.AGENT_ACTION_DIM))
    agent_action[4] = agent_action[4].strip(')')

    agent_action[1] = map_cs(agent_action[1])
    agent_action[3] = map_cs(agent_action[3])
    agent_action[2] = map_agent_ts_str(agent_action[2])

    if agent_action[2] in ['request(last_movie)', 'request(reason_like)', 'request(genre)', 'request(actor)', 'request(director)', 'inform(movie)', 'request(reason_not_like)']:
        agent_action[3] = 'QESD'
    if agent_action[2] in ['inform(actor)', 'inform(genre)', 'inform(movie_info)', 'request(feedback)']:
        agent_action[3] = 'NONE'
    agent_action = tuple(agent_action)
    return agent_action


def map_cs(cs):
    """
    :param cs: Convert the CS into something the user simulator and state tracker recognize.
    :return:
    """
    if cs not in config.ALL_CONV_STRATEGIES:
        return config.ALL_CONV_STRATEGIES[-1]
    else:
        return cs


def map_agent_ts_str(agent_ts_str):
    if agent_ts_str == 'request(why)':
        agent_ts_str = 'request(reason_not_like)'
    elif agent_ts_str == 'request(another)':
        agent_ts_str = 'request(another_one)'
    elif agent_ts_str == 'inform(plot)':
        agent_ts_str = 'inform(movie_info)'
    return agent_ts_str