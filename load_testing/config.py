import yaml
import os


def read_config():
    with open(os.getcwd() + "/config.yaml") as f:
        config = yaml.safe_load(f)
    with open(config["queries_file"]) as f:
        queries = f.read().splitlines()
        config["queries"] = queries
    return config


config = read_config()
