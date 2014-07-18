import os
import yaml
from schema import Use, Schema, SchemaError


class InvalidConfig(Exception):
    pass


class MissingConfig(Exception):
    pass


default_config = {}
schema = Schema({
    'stellar_url': Use(str),
    'url': Use(str),
    'project_name': Use(str),
    'tracked_databases': [Use(str)]
})


def load_config():
    config = {}
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
            break

    if not config:
        raise MissingConfig()

    for k, v in default_config.items():
        if k not in config:
            config[k] = v

    try:
        return schema.validate(config)
    except SchemaError, e:
        raise InvalidConfig(e)
