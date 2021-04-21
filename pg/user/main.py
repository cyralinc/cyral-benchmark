import typer
import pg
from helpers import pretty_print_results

app = typer.Typer()


@app.command()
def load_test(type: str = "pg"):
    if type == "pg":
        average_latencies = pg.load_test()
    else:
        raise Exception(f"load testing is not supported yet for '{type}' repos")
    pretty_print_results(average_latencies)


if __name__ == "__main__":
    app()
