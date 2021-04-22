from prettytable import PrettyTable
from config import config


def pretty_print_results(tests_average_latency_per_query):
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
    # transpose input as the input represnt the columns of the table
    table_rows = [list(x) for x in zip(*tests_average_latency_per_query)]
    for index, row in enumerate(table_rows):
        table.add_row([f"Query #{index+1}"] + [f"{round(cell, 4):.4f} ms" for cell in row])
    # average latency per test
    average_test_latency = [sum(column)/len(column) for column in tests_average_latency_per_query]
    table.add_row([f"All"] + [f"{round(cell, 4):.4f} ms" for cell in average_test_latency])
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
