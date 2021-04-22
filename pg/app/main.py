import concurrent.futures
import os
import re
import statistics
import subprocess
import sys
import threading
import time
import typing
import yaml
from tqdm import tqdm

def parse_pgbench_output(output: str):
    parsed_output = {}

    match = re.search(r'number of transactions actually processed: ([\d]+)', output)
    if not match:
        raise Exception(f'Unable to parse output: number of transactions actually processed was not found. Output: {output}')
    try:
        parsed_output['transactions'] = int(match.group(1))
    except Exception:
        parsed_output['transactions'] = -1
    if parsed_output['transactions'] <= 0:
        raise Exception('pgbench reported no transactions processed. Try decreasing concurrent_instances or connection_pool_size.')

    match = re.search(r'latency average = ([\d\.]+)', output)
    if not match:
        raise Exception(f'Unable to parse output: average latency not found. Output: {output}')
    try:
        parsed_output['latency'] = float(match.group(1))
    except Exception:
        parsed_output['latency'] = -1

    match = re.search(r'tps = ([\d\.]+) \(excluding connections establishing\)', output)
    if not match:
        raise Exception(f'Unable to parse output: TPS value not found. Output: {output}')
    try:
        parsed_output['tps'] = float(match.group(1))
    except Exception:
        parsed_output['tps'] = -1

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

    futures, results, exceptions = [], [], []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(run_pgbench, id, pgbench_args)
            for id in range(app_config['concurrent_instances'])
        ]
        for i in tqdm(range(app_config['duration'])):
            if not any([f.running() for f in futures]):
                break
            time.sleep(1)
        if any([f.running() for f in futures]):
            print("Waiting for pgbench instances to finish...")
        results = [f.result() for f in futures]
        exceptions = [f.exception() for f in futures]

    if any(exceptions):
        sys.exit(f'at least one pgbench instance has terminated with error: {exceptions}')

    try:
        results = [parse_pgbench_output(r) for r in results]
    except Exception as err:
        sys.exit(err)
    
    latency_values = [r['latency'] for r in results if r['latency'] != -1]
    tps_values = [r['tps'] for r in results if r['tps'] != -1]

    print()
    if latency_values:
        print('Average latency: {} ms'.format(statistics.mean(latency_values)))
    if tps_values:
        print('Average TPS: {}'.format(statistics.mean(tps_values)))

if __name__ == '__main__':
    main()