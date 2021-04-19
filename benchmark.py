import argparse
import concurrent.futures
import re
import statistics
import subprocess
import threading
import time
import typing

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
        print(f"Unable to parse pgbench output: {e}")
        parsed_output = {}
    return parsed_output

def run_pgbench(args: typing.List[str]):
    print("starting app instance")
    command = ["pgbench"]
    command += args
    result = subprocess.run(command, capture_output=True)
    return str(result.stdout, 'utf-8')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, required=True)
    parser.add_argument('--user', type=str, required=True)
    parser.add_argument('--concurrent-instances', type=int, default=10, help="number of concurrent instances of pgbench to run")
    parser.add_argument('--duration', type=int, default=300, help="duration (in seconds) of each pgbench benchmark")
    parser.add_argument('--load-script', type=str, choices=['tpcb-like', 'select-only'], default='tpcb-like')
    parser.add_argument('--protocol', type=str, choices=['simple', 'prepared'], default='simple')
    args = parser.parse_args()

    results = []
    pgbench_args = [
        '-h', f'{args.host}', '-U', f'{args.user}', '--client=128', '--jobs=128',
        f'--time={args.duration}', f'--builtin={args.load_script}', f'--protocol={args.protocol}'
    ]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(run_pgbench, pgbench_args) for i in range(10)]
        results = [f.result() for f in futures]
        results = [parse_pgbench_output(r) for r in results]
    
    print(
        "Average latency: {} ms".format(
            statistics.mean([r['latency_average'] for r in results])
        )
    )
    print(
        "Average TPS: {}".format(
            statistics.mean([r['tps_excluding_connections_establishing'] for r in results])
        )
    )

if __name__ == '__main__':
    main()