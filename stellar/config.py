import os
import yaml

default_config = {
    'stellar_url': 'postgresql://localhost:5432/stellar_data',
    'url': 'postgresql://localhost:5432/',
    'tracked_databases': ['pelsu']
}


def load_config():
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

    for name in ['tracked_databases', 'project_name']:
        if not config or not name in config:
            raise Exception('Configuration variable %s is not set.' % name)

    for k, v in default_config.items():
        if k not in config:
            config[k] = v
    return config


class Config(object):
    config = None

    def __getitem__(self, key):
        if not self.config:
            self.config = load_config()
            if not self.config:
                raise Exception(
                    "Couldn't find project configuration file stellar.yaml"
                )

        return self.config[key]


config = Config()
