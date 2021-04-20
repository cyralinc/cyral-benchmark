from prettytable import PrettyTable
from config import config

def print_results_table(average_latencies):
    print("Summary:")
    table = PrettyTable(
        ["", "no. of sessions", f"average latency for {config['runs_per_test']} runs"]
    )
    for ind, (test_no_of_sessions, average_latency) in enumerate(
        zip(config["sessions_per_test"], average_latencies)
    ):
        table.add_row([f"Test #{ind+1}", test_no_of_sessions, f"{average_latency} ms"])
    print(table)


def parse_pgbench_output(pgbench_output):
    parsed = {}
    for output_line in pgbench_output.splitlines():
        if ":" in output_line:
            splitted_line = output_line.split(":")
        elif "=" in output_line:
            splitted_line = output_line.split("=")
        else:
            raise Exception("output cannot be parsed, output:" + pgbench_output)
        parsed[splitted_line[0].strip()] = splitted_line[1].strip()
    return parsed