import yaml
import re

CONFIG_PATH = "config.yml"


def resolve_variables(config):
    resolved_config = {}
    for key, value in config.items():
        if isinstance(value, str):
            matches = re.findall(r'\${(\w+)}', value)
            for match in matches:
                if match in config:
                    value = value.replace(f'${{{match}}}', str(config[match]))
        resolved_config[key] = value
    return resolved_config


def load_config():
    with open(CONFIG_PATH, 'r') as config_file:
        config = yaml.safe_load(config_file)
    return resolve_variables(config)


def get_config_value(key):
    config = load_config()
    return config.get(key)
