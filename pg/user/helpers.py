from prettytable import PrettyTable
from config import config


def pretty_print_results(average_latencies_per_test):
    # printing test queries
    print("\nQueries used:\n")
    for index, query in enumerate(config["queries"]):
        print(f"Query #{index+1}: '{query}'")
    # preparing table 
    print("\nAverage Latencies:\n")
    titles_row = []
    for no_of_users in config["concurrent_users"]:
        titles_row.append(f"{no_of_users} concurrent users")
    table = PrettyTable([""] + titles_row)
    for key, latencies in average_latencies_per_test.items():
        table.add_row([key] + [f"{round(val, 4):.4f} ms" for val in latencies])
    # printing table
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


def get_millisec(formatted_time):
    """time is assumed to be formatted as hh:mm:ss"""
    splitted = formatted_time.split(":")
    h, m, s =  splitted if len(splitted) is 3 else ([0] + splitted)
    return 1000 * (int(h) * 3600 + int(m) * 60 + int(s))
