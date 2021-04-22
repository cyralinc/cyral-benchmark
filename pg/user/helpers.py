from prettytable import PrettyTable
from config import config


def pretty_print_results(tests_average_latency_per_query):
    # printing test queries
    print("\nQueries used:\n")
    for index, query in enumerate(config["queries"]):
        print(f"Query #{index+1}: '{query}'")
    print("\nAverage Latencies:\n")
    # preparing table
    # table example:
    # +----------+---------------------+---------------------+
    # |          | 10 concurrent users | 20 concurrent users |
    # +----------+---------------------+---------------------+
    # | Query #1 |      3.0363 ms      |      3.6066 ms      |
    # | Query #2 |      2.5981 ms      |      3.3717 ms      |
    # | Query #3 |      5.0235 ms      |      6.3476 ms      |
    # | Query #4 |      26.0987 ms     |      33.0589 ms     |
    # | Query #5 |     237.2720 ms     |     275.7278 ms     |
    # |   All    |      54.8057 ms     |      64.4225 ms     |
    # +----------+---------------------+---------------------+
    titles_row = []
    for no_of_users in config["concurrent_users"]:
        titles_row.append(f"{no_of_users} concurrent users")
    table = PrettyTable([""] + titles_row)
    # transpose input as the input represnt the columns of the table
    table_rows = [list(x) for x in zip(*tests_average_latency_per_query)]
    for index, row in enumerate(table_rows):
        table.add_row(
            [f"Query #{index+1}"] + [f"{round(cell, 4):.4f} ms" for cell in row]
        )
    # average latency per test
    average_test_latency = [
        sum(column) / len(column) for column in tests_average_latency_per_query
    ]
    table.add_row(
        ["All"] + [f"{round(cell, 4):.4f} ms" for cell in average_test_latency]
    )
    # printing table
    print(table)


def get_millisec(formatted_time):
    splitted = formatted_time.split(":")
    h, m, s = splitted if len(splitted) == 3 else ([0] + splitted)
    return 1000 * (int(h) * 3600 + int(m) * 60 + int(s))


def add_lists(list1, list2):
    if len(list1) != len(list2):
        raise Exception("Cannot add lists!")
    return [item1 + item2 for item1, item2 in zip(list1, list2)]
