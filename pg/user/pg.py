import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from config import config, db_config
from helpers import parse_pgbench_output, get_millisec


def extract_latencies(psql_output):
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
    psql_command = f"psql \
                    -h {db_config['host']} \
                    -p {db_config['port']} \
                    -U {db_config['username']} \
                    -d {db_config['db']} \
                    -c '\\pset pager 0' \
                    -c '\\timing on' "
    for query in config["queries"]:
        psql_command += f" -c '{query}'"
    os.environ['PGPASSWORD'] = db_config['password']
    psql_output = subprocess.run(
        psql_command,
        shell=True,
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8")
    latencies = extract_latencies(psql_output)
    return latencies


<<<<<<< HEAD
def get_average_query_latency_per_request(requests):
    total_queries_latencies = []
=======
def get_average_query_latency_per_request(query, requests):
    total_latency = 0.0
>>>>>>> main
    for _ in range(requests):
        try:
            user_queries_latencies = run_queries()
            total_queries_latencies = user_queries_latencies if not len(total_queries_latencies) else [item1+item2 for item1, item2 in zip(user_queries_latencies, total_queries_latencies)]
        except subprocess.CalledProcessError as err:
            raise Exception(f"psql terminated with error: {str(err.stderr, 'utf-8')}")
        # latency time should be the last line in the psql output
    average_latencies_per_request = [item / requests for item in total_queries_latencies]
    return average_latencies_per_request


def get_queries_average_latency_per_user(no_of_users, requests, pbar):
    total_latencies = []
    with ThreadPoolExecutor(max_workers=no_of_users) as e:
        future_query_latencies = [
            e.submit(get_average_query_latency_per_request, requests)
            for _ in range(no_of_users)
        ]
        for future_query_latency in future_query_latencies:
            user_queries_latencies = future_query_latency.result()
            total_latencies = user_queries_latencies if not len(total_latencies) else [item1+item2 for item1, item2 in zip(total_latencies, user_queries_latencies)]
            pbar.update(1)
    average_latencies = [item / no_of_users for item in total_latencies]
    return average_latencies


def load_test():
    tests_average_latency_per_query = []
    concurrent_users = config["concurrent_users"]
    queries = config["queries"]
    with tqdm(total=sum(concurrent_users), desc="Running...") as pbar:
        for no_of_users in concurrent_users:
            queries_average_latency = get_queries_average_latency_per_user(
                no_of_users, config["nb_requests"], pbar
            )
            tests_average_latency_per_query.append(queries_average_latency)
        return tests_average_latency_per_query
