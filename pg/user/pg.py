import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from tqdm import tqdm
from config import config, db_config
from helpers import parse_pgbench_output, get_millisec


def run_command(command):
    psql_command = f"psql \
                    -h {db_config['host']} \
                    -p {db_config['port']} \
                    -U {db_config['username']} \
                    -d {db_config['db']} \
                    -c '\\timing on' \
                    -c '{command}'"
    psql_output = subprocess.run(
        psql_command,
        shell=True,
        capture_output=True,
        check=True,
        env={"PGPASSWORD": db_config["password"]},
    ).stdout.decode("utf-8")
    return psql_output


def get_average_query_latency_per_run(query, runs):
    total_latency = 0.0
    for _ in range(runs):
        try:
            psql_output = run_command(query)
        except subprocess.CalledProcessError as err:
            raise Exception(f"psql terminated with error: {str(err.stderr, 'utf-8')}")
        # latency time should be the last line in the psql output
        timinig_info = psql_output.splitlines()[-1]
        latency_in_ms = (
            float(timinig_info.split()[1])
            if "ms" in timinig_info
            else get_millisec(timinig_info.split()[1])
        )
        total_latency += latency_in_ms
    return total_latency / runs


def get_query_average_latency_per_session(no_of_sessions, query, runs):
    total_latency = 0.0
    with ThreadPoolExecutor(max_workers=no_of_sessions) as e:
        future_query_latencies = [
            e.submit(get_average_query_latency_per_run, query, runs)
            for _ in range(no_of_sessions)
        ]
        for future_query_latency in future_query_latencies:
            total_latency += future_query_latency.result()
    return total_latency / no_of_sessions


def load_test():
    average_latency_per_query = defaultdict(list)
    average_latency_per_test = []
    concurrent_users = config["concurrent_users"]
    queries = config["queries"]
    with tqdm(total=len(concurrent_users)*len(queries), desc="Running...") as pbar:
        for no_of_sessions in concurrent_users:
            test_total_latency = 0.0
            for ind, query in enumerate(queries):
                average_query_latency = get_query_average_latency_per_session(
                    no_of_sessions, query, config["nb_requests"]
                )
                average_latency_per_query[f"Query #{ind+1}"].append(average_query_latency)
                test_total_latency += average_query_latency
                pbar.update(1)
            average_latency_per_test.append(test_total_latency / len(config["queries"]))
        average_latency_per_query["All"] = average_latency_per_test
        return average_latency_per_query
