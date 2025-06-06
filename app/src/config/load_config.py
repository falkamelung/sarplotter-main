import os
import json5


def loadConfig(config_file_name='config.json'):
    """

    :return:
    """
    script_dir = os.path.dirname(__file__)
    config_path = os.path.join(script_dir, '../..', 'config', config_file_name)
    with open(config_path, "r") as file:
        config = json5.load(file)
    return config
