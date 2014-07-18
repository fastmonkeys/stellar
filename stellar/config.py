import os
import yaml

default_config = {}


def load_config():
    config = None
    current_directory = os.getcwd()
    while True:
        try:
            with open(
                os.path.join(current_directory, 'stellar.yaml'),
                'rb'
            ) as fp:
                config = yaml.safe_load(fp)
                break
        except IOError:
            pass
        current_directory = os.path.abspath(
            os.path.join(current_directory, '..')
        )

        if current_directory == '/':
            return

    if not config:
        raise Exception(
            "Couldn't find project configuration file stellar.yaml"
        )

    for k, v in default_config.items():
        if k not in config:
            config[k] = v

    for name in ['tracked_databases', 'project_name']:
        if not config or not name in config:
            raise Exception('Configuration variable %s is not set.' % name)

    return config
