from src import config


def read_nlg_db(file_path, num_fields_keys):
    nlg_db = {}

    with open(file_path, 'r', encoding='UTF-8') as f:
        all_lines = f.readlines()
        for i, line in enumerate(all_lines):
            line = line.rstrip('\n').split(config.FILE_DELIMITER)
            if i == 0:
                header = line[num_fields_keys:]
            else:
                key = tuple(line[:num_fields_keys])
                value = line[num_fields_keys:]
                assert len(header) == len(value)
                nlg_db[key] = dict(zip(header, value))

    return nlg_db
