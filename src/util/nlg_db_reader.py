from src import config


def read_nlg_db(file_path, num_fields_keys):
    if num_fields_keys < config.NUM_FIELDS_NLG_USER:
        raise ValueError("%d less than expected: %d." % (num_fields_keys, config.NUM_FIELDS_NLG_USER))

    nlg_db = {}

    with open(file_path, 'r', encoding='UTF-8') as f:
        all_lines = f.readlines()
        for i, line in enumerate(all_lines):
            line = line.rstrip('\n').split(config.FILE_DELIMITER)
            if i == 0:
                header = line[num_fields_keys:]
            else:
                second_field_list = line[1].split(config.OPTIONS_DELIMITER)
                for sf in second_field_list:
                    key = (line[0], sf.strip(' ""'), *line[2:num_fields_keys])
                    value = line[num_fields_keys:]
                    assert len(header) == len(value)
                    nlg_db[key] = dict(zip(header, value))

    return nlg_db
