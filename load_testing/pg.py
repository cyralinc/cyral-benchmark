import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from config import config
from helpers import parse_pgbench_output, get_millisec


def run_command(command):
    db_config = config["db_config"]
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
    totol_latency = 0.0
    for _ in range(runs):
        psql_output = run_command(query)
        # latency time should be the last line in the psql output
        timinig_info = psql_output.splitlines()[-1]
        latency_in_ms = (
            float(timinig_info.split()[1])
            if "ms" in timinig_info
            else get_millisec(timinig_info.split()[1])
        )
        totol_latency += latency_in_ms
    return totol_latency / runs


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
    average_latencies = []
    for test_index, no_of_sessions in enumerate(config["sessions_per_test"]):
        print(f"Test #{test_index+1}: no. of sessions = {no_of_sessions}")
        sum_of_average_queries_latencies = 0.0
        for query_index, query in enumerate(config["queries"]):
            print(
                f"\tQuery #{query_index+1}: \n\t\tquery: {query} \n\t\taverage latency = ",
                end=" ",
            )
            average_query_latency = get_query_average_latency_per_session(
                no_of_sessions, query, config["runs_per_query"]
            )
            print(f"{average_query_latency} ms")
            sum_of_average_queries_latencies += average_query_latency
        average_test_latency = sum_of_average_queries_latencies / len(config["queries"])
        average_latencies.append(average_test_latency)
        print(f"average test latency = {average_test_latency} ms")
    return average_latencies
