from src import config


def get_agent_scenario(file_path):
    agent_reasoner = {}
    pass
    agent_reasoner[config.ACK_STR] = {}
    agent_reasoner[config.OTHER_STR] = {}

    with open(file_path, 'r', encoding='UTF-8') as f:
        all_lines = f.readlines()

        for i, line in enumerate(all_lines):
            line = line.rstrip('\n').rstrip(config.FILE_DELIMITER).split(config.FILE_DELIMITER)

            if i != 0:
                # Construct agent reasoner.
                task_strategies = line[config.AGENT_KEY].split(config.OPTIONS_DELIMITER)
                conv_strategies = line[config.AGENT_KEY + config.NUM_FIELDS_KEYS - 1].split(config.OPTIONS_DELIMITER)

                for ts in task_strategies:
                    ts = ts.strip(' ""')
                    for cs in conv_strategies:
                        cs = cs.strip(' ""')

                        context = line[config.CONTEXT_KEY].strip(' ""')
                        pre_condition_key = (context, ts, cs)

                        post_condition_key = line[config.AGENT_KEY + config.NUM_FIELDS_KEYS]
                        if post_condition_key == config.ACK_STR:
                            reasoner_key = config.ACK_STR
                        else:
                            reasoner_key = config.OTHER_STR

                        if pre_condition_key not in agent_reasoner[reasoner_key]:
                            agent_reasoner[reasoner_key][pre_condition_key] = {}

                        if post_condition_key not in agent_reasoner[reasoner_key][pre_condition_key]:
                            agent_reasoner[reasoner_key][pre_condition_key][post_condition_key] = []

                        agent_conv_strategies = line[config.AGENT_KEY + 2 * config.NUM_FIELDS_KEYS - 1].split(config.OPTIONS_DELIMITER)
                        for acs in agent_conv_strategies:
                            agent_reasoner[reasoner_key][pre_condition_key][post_condition_key].append(acs.strip(' ""'))
    return agent_reasoner


def get_user_sim_scenario(file_path):
    user_simulator_reasoner = {}

    with open(file_path, 'r', encoding='UTF-8') as f:
        all_lines = f.readlines()

        for i, line in enumerate(all_lines):
            line = line.rstrip('\n').rstrip(config.FILE_DELIMITER).split(config.FILE_DELIMITER)

            if i != 0:
                # Construct user reasoner.
                conv_strategies = line[config.USER_KEY + config.NUM_FIELDS_KEYS - 1].split(config.OPTIONS_DELIMITER)
                ts = line[config.USER_KEY].strip(' ""')
                if ts != config.ACK_STR:
                    for cs in conv_strategies:
                        cs = cs.strip(' ""')

                        pre_condition_key = (ts, cs)

                        if pre_condition_key not in user_simulator_reasoner:
                            user_simulator_reasoner[pre_condition_key] = {}

                        for j in range(config.USER_KEY + config.NUM_FIELDS_KEYS, len(line), config.NUM_FIELDS_KEYS):
                            post_condition_key = line[j].strip(' ""')
                            if post_condition_key not in user_simulator_reasoner[pre_condition_key]:
                                user_simulator_reasoner[pre_condition_key][post_condition_key] = []

                            user_conv_strategies = line[j + 1].split(config.OPTIONS_DELIMITER)
                            for ucs in user_conv_strategies:
                                ucs = ucs.strip(' ""')
                                user_simulator_reasoner[pre_condition_key][post_condition_key].append(ucs)
    return user_simulator_reasoner
