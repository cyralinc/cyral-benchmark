import yaml
import os


def read_config():
    with open(os.getcwd() + "/config.yaml") as f:
        config = yaml.safe_load(f)
        return config


config = read_config()
