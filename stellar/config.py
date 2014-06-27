import yaml

default_config = {
    'stellardb': 'stellardb'
}

with open("~/.stellar.yaml", 'rb') as fp:
    config = yaml.safe_load(fp)
    for k, v in default_config.items():
        if k not in config:
            config[k] = v
