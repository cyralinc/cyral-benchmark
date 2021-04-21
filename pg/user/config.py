import yaml
import os


def read_config():
    with open("/config.yaml") as f:
        temp = yaml.safe_load(f)
    config = temp["user_load_testing_config"]
    with open(config["queries_file"]) as f:
        queries = [query for query in f.read().splitlines() if not query.startswith("--")]
        config["queries"] = queries
    return config, temp["db_config"]


config, db_config = read_config()
