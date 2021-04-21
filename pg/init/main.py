import os
import subprocess
import typing
import yaml

def run_pgbench(args: typing.List[str]):
    command = ['pgbench']
    command += args
    result = subprocess.run(command, capture_output=True)
    if result.returncode != 0:
        stderr = str(result.stderr, 'utf-8')
        raise Exception(f'pgbench terminated with a non-zero code. stderr: {stderr}')
    return str(result.stdout, 'utf-8')

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

    output = run_pgbench(pgbench_args)
    print(output)

if __name__ == '__main__':
    main()