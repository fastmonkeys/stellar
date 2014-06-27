import os
import yaml

default_config = {
    'stellar_url': 'postgresql://localhost:5432/stellar_data',
    'url': 'postgresql://localhost:5432/',
    'tracked_databases': ['pelsu']
}

current_directory = os.getcwd()
while True:
    try:
        with open(os.path.join(current_directory, 'stellar.yaml'), 'rb') as fp:
            config = yaml.safe_load(fp)
            break
    except IOError:
        pass
    current_directory = os.path.abspath(os.path.join(current_directory, '..'))

    if current_directory == '/':
        raise Exception('stellar.yaml not found')

for k, v in default_config.items():
    if k not in config:
        config[k] = v

if not 'tracked_databases' in config:
    raise Exception('Configuration variable tracked_databases is not set.')
