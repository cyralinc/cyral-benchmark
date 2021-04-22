import concurrent.futures
import os
import re
import statistics
import subprocess
import threading
import time
import typing
import yaml
from tqdm import tqdm

def parse_pgbench_output(output: str):
    parsed_output = {}
    try:
        parsed_output['transactions_actually_processed'] = int(
            re.search(r'number of transactions actually processed: ([\d]+)', output).group(1)
        )
        parsed_output['latency_average'] = float(
            re.search(r'latency average = ([\d\.]+)', output).group(1)
        )
        parsed_output['tps_including_connections_establishing'] = float(
            re.search(r'tps = ([\d\.]+) \(including connections establishing\)', output).group(1)
        )
        parsed_output['tps_excluding_connections_establishing'] = float(
            re.search(r'tps = ([\d\.]+) \(excluding connections establishing\)', output).group(1)
        )
    except Exception as e:
        raise Exception(f'Unable to parse pgbench output.\nOutput: {output}\nError: {e}.')
    return parsed_output

def run_pgbench(id: int, args: typing.List[str]):
    command = ['pgbench']
    command += args
    result = subprocess.run(command, capture_output=True)
    if result.returncode != 0:
        stderr = str(result.stderr, 'utf-8')
        raise Exception(f'pgbench #{id} terminated with a non-zero code. stderr: {stderr}')
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
        f'--client={app_config["connection_pool_size"]}',
        f'--jobs={app_config["connection_pool_size"]}',
        f'--time={app_config["duration"]}',
        f'--builtin={app_config["load_script"]}',
        f'--protocol={app_config["protocol"]}'
    ]
    os.environ['PGPASSWORD'] = db_config['password']

    results, exceptions = [], []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(run_pgbench, id, pgbench_args)
            for id in range(app_config['concurrent_instances'])
        ]
        for i in tqdm(range(app_config['duration'])):
            if not any([f.running() for f in futures]):
                break
            time.sleep(1)
        results = [f.result() for f in futures]
        exceptions = [f.exception() for f in futures]

    if any(exceptions):
        raise Exception(f'at least one pgbench instance has terminated with error: {exceptions}')

    results = [parse_pgbench_output(r) for r in results]
    print(
        'Average latency: {} ms'.format(
            statistics.mean([r['latency_average'] for r in results])
        )
    )
    print(
        'Average TPS: {}'.format(
            statistics.mean([r['tps_excluding_connections_establishing'] for r in results])
        )
    )

if __name__ == '__main__':
    main()