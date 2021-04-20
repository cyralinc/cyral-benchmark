# Run load testing

1. Activate virtualenv for this project: `poetry shell`
2. Install dependencies: `poetry install` 
3. Update db_config in `load_testing/config.yaml`
4. (optionally) update testing config in `load_testing/config.yaml`
5. (optionally) update test queries in `load_testing/test_queries.psql` or specify a sql file in setp 4
4. Run `python3 load_testing/main.py`