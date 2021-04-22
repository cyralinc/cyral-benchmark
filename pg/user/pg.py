import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from config import config, db_config
from helpers import get_millisec, add_lists


def extract_latencies(psql_output):
    """
    extracts the time latencies from a psql_output
    """
    latencies = []
    for line in psql_output.splitlines():
        if line.startswith("Time:"):
            latency_in_ms = (
                float(line.split()[1])
                if "ms" in line
                else get_millisec(line.split()[1])
            )
            latencies.append(latency_in_ms)
    return latencies


def run_queries():
    """
    runs all the predefined queries in a single psql command
    """
    psql_command = f"psql \
                    -h {db_config['host']} \
                    -p {db_config['port']} \
                    -U {db_config['username']} \
                    -d {db_config['db']} \
                    -c '\\pset pager 0' \
                    -c '\\timing on' "
    for query in config["queries"]:
        psql_command += f" -c '{query}'"
    os.environ["PGPASSWORD"] = db_config["password"]
    psql_output = subprocess.run(
        psql_command,
        shell=True,
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8")
    return psql_output


def get_queries_average_latencies_per_request(nb_requests):
    """
    runs all the predefined queries 'nb_requests' times and returns the average latenceis per request
    """
    total_queries_latencies = []
    for _ in range(nb_requests):
        try:
            psql_output = run_queries()
            queries_latencies = extract_latencies(psql_output)
            total_queries_latencies = (
                queries_latencies
                if not len(total_queries_latencies)
                else add_lists(total_queries_latencies, queries_latencies)
            )
        except subprocess.CalledProcessError as err:
            raise Exception(f"psql terminated with error: {str(err.stderr, 'utf-8')}")
    average_queries_latencies_per_request = [
        total_query_latencies / nb_requests
        for total_query_latencies in total_queries_latencies
    ]
    return average_queries_latencies_per_request


def get_queries_average_latencies_per_user(no_of_users, nb_requests, pbar):
    """
    parallelly runs 'no_of_users' threads and returns the average latencies experienced by each one
    """
    total_latencies = []
    with ThreadPoolExecutor(max_workers=no_of_users) as e:
        future_queries_latencies = [
            e.submit(get_queries_average_latencies_per_request, nb_requests)
            for _ in range(no_of_users)
        ]
        for future in future_queries_latencies:
            queries_latencies = future.result()
            total_latencies = (
                queries_latencies
                if not len(total_latencies)
                else add_lists(total_latencies, queries_latencies)
            )
            pbar.update(1)
    average_latencies = [
        total_latency / no_of_users for total_latency in total_latencies
    ]
    return average_latencies


def load_test():
    """
    runs the user load test
    """
    tests_average_latencies = []
    concurrent_users = config["concurrent_users"]
    with tqdm(total=sum(concurrent_users), desc="Running...") as pbar:
        for no_of_users in concurrent_users:
            # each item in 'concurrent_users' list represents a test
            # given a set of concurrent users in a test, compute the average experienced latency for each query
            queries_average_latencies = get_queries_average_latencies_per_user(
                no_of_users, config["nb_requests"], pbar
            )
            tests_average_latencies.append(queries_average_latencies)
        return tests_average_latencies
