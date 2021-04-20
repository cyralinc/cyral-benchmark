# Run load testing

1. Activate virtualenv for this project: `poetry shell`
2. Install dependencies: `poetry install` 
3. Update db_config in `load_testing/config.yaml`
4. Run `python3 load_testing/main.py`