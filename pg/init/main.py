import os
import subprocess
import typing
import yaml

def run_pgbench(args: typing.List[str]):
    command = ['pgbench']
    command += args
    subprocess.run(command, check=True)

def parse_config():
    config = {}
    with open('/config.yaml') as f:
        config = yaml.safe_load(f)
    # TODO: raise exceptions when the config is not valid
    return config

def main():
    config = parse_config()
    db_config = config['db_config']
    app_config = config['app_load_testing_config']

    pgbench_args = [
        '-h', f'{db_config["host"]}',
        '-U', f'{db_config["username"]}',
        '--initialize',
        f'--scale={app_config["concurrent_instances"]*app_config["connection_pool_size"]}',
    ]
    os.environ['PGPASSWORD'] = db_config['password']

    run_pgbench(pgbench_args)

if __name__ == '__main__':
    main()