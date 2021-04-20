
import os
import subprocess
import typer
from config import config
from helpers import parse_pgbench_output, print_results_table

app = typer.Typer()


def load_test_pg():
    average_latencies = []
    db_config = config["db_config"]
    for index, no_of_sessions in enumerate(config["sessions_per_test"]):
        print(f"Test #{index+1}: no. of sessions = {no_of_sessions}")
        total_latency = 0.0
        for run in range(config["runs_per_test"]):
            print(f"\tRun #{run+1}: average latency = ", end=" ")
            pgbench_command = f"pgbench \
                                -h {db_config['host']} \
                                -p {db_config['port']} \
                                -U {db_config['username']} \
                                -c {no_of_sessions} \
                                -j {no_of_sessions} \
                                -n \
                                -f {config['transaction_file']} \
                                {db_config['db']}"
            pgbench_output = subprocess.run(
                pgbench_command.split(),
                capture_output=True,
                check=True,
                env={"PGPASSWORD":db_config["password"]}
            ).stdout.decode("utf-8")
            parsed_pgbench_output = parse_pgbench_output(pgbench_output)
            run_latency = float(parsed_pgbench_output["latency average"].split()[0])
            total_latency += run_latency
            print(f"{run_latency} ms")

        average_latency = total_latency / config["runs_per_test"]
        average_latencies.append(average_latency)
        print(f"\taverage latency = {average_latency} ms")
    return average_latencies


@app.command()
def load_test(type: str = "pg"):
    if type == "pg":
        average_latencies = load_test_pg()
    else:
        raise Exception(f"load testing is not supported yet for '{type}' repos")
    print_results_table(average_latencies)


if __name__ == "__main__":
    app()
