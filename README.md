# Cyral benchmarking tool
This is a tool for benchmarking database throughput and request latency. You can use it to quantify the impact of enabling and disabling various levels of Cyral protection on a sample database. You can configure a test to connect directly to the database, or through the Cyral sidecar. 

# Usage

## Prerequisites
- Make sure your PostgreSQL server is accessible to the test environment.
- By default the tool depends on datasets created by pgbench. Before running a load test, you must run the [initialization step](#Initialization) to create these datasets.
- Provide user credentials of a user who can perform DDL and DML actions there.
- Install and configure a Cyral sidecar that allows access to the database using the credentials you’ve supplied for the test.
- To use the same credentials for testing with and without the sidecar, make sure **Allow native authentication** is enabled for the repo. You can set this in the Cyral control plane UI.


## Initialization
The tool provides an `init` function to populate your PostgreSQL database with sample data using [pgbench](https://www.postgresql.org/docs/10/pgbench.html). This only has to be done once for each repository you run the tests against.
```
docker run -v path/to/local/config.yaml:/config.yaml gcr.io/cyralinc/cyral-benchmark:v0.1.0 init
```

## Application load testing
The app load testing tool simulates a large number of connection pools originating from multiple applications by making requests through `pgbench`. It measures transactions per second (TPS) and latency for each application and outputs these metrics in an aggregated form. Please see [Configuration](#Configuration) for instructions on how to configure this test.
```
docker run -v path/to/local/config.yaml:/config.yaml gcr.io/cyralinc/cyral-benchmark:v0.1.0 app
```

## User load testing
The user load testing tool emulates the latency an adhoc user would experience when making requests through `psql`. It measures request latency for a each of a configurable set of queries, under load conditions that represent various numbers of concurrent database connections. Please see [Configuration](#Configuration) for instructions on how to configure this test. 
```
docker run -v path/to/local/config.yaml:/config.yaml gcr.io/cyralinc/cyral-benchmark:v0.1.0 user
```

# Configuration
For all use cases (initialization, application load testing, or user load testing), you configure the tool by specifying values in a `config.yaml` file that you'll pass to the Docker image. Here's a sample configuration file:
```
db_config:
  host:
  port: 
  db: 
  username: 
  password: 

user_load_testing_config:
  concurrent_users: [10, 100, 1000]  
  nb_requests: 100 
  queries_file: ./test_queries.sql

app_load_testing_config:
  concurrent_instances: 10
  connection_pool_size: 128
  duration: 300
  load_script: tpcb-like
  protocol: prepared
```

The `db_config` field is where you'll specify connection details for the database that the tests will be run against. All of these fields are required for initialization, application load testing, and user load testing.
- **host (string):** The host address of your database
- **port (number):** The port at which the database is listening for connections
- **db (string):** The name of the already created database to connect to
- **username (string):** The database user to connect with. Use a native repository user account, not an SSO user, as the username for the test.
- **password (string):** The password for the specified database user

The `user_load_testing_config` field is optional and provides fields for configuring the user load test:
- **concurrent_users (\[number\]):** Numbers of concurrent users to simulate for each query.
- **nb_requests (number):** Number of times to run each specified query for each concurrent users -- latencies will be averaged over this number of requests.
- **queries_file (string):** Path to a file containing the set of queries to run in the test (default: `./test_queries.sql`). This file is only used in `user` tests.

The `app_load_testing_config` field is optional and provides fields for configuring the application load test:
- **concurrent_instances (number):** Number of concurrent instances of pgbench to run. Default: `10`.
- **connection_pool_size (number):** Number of connections to start on each pgbench instance. Default: `128`.
- **duration (number):** Duration (in seconds) of the pgbench trial (default: `300`)
- **load_script (string):** Built-in script of pgbench to run. Supported values are `tpcb-like` and `select-only`. Default: `tpcb-like`.
- **protocol (string):** Protocol to use for submitting queries to the server. Supported values are `simple` and `prepared`. Default: `prepared`.