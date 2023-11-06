# Introduction
This project downloads data from the [CBS Statline API](https://opendata.cbs.nl/statline/portal.html?_la=nl&_catalog=CBS&tableId=03759ned&_theme=269) and provides an analyis of growth of the Dutch population in contrast to the growth of a specific type of ground usage, such as agriculture or living space. The data is firstly downloaded and saved as a .parquet file in the `data/parquet` folder. Secondly, the data is processed and saved to a PostgreSQL database. Lastly, a streamlit dashboard is provided to visualize the data and also validate the created models.

## Requirements
The following requirements are needed to run the program;
- Docker, either the desktop version or the CLI version
- Python 3.11 or higher
- PDM
- Make

## Setup
To setup the program, run the following command;
```
make init
```
This will install the required packages and creates the required folders. Make sure to adjust the `.env` file to your liking, this will contain the database credentials.

## Usage
The makefile abstract certain commands for ease of use. The following commands are available, described below but also under the `help` command;
```
make help
```
Displays the help menu
```
make init
```
Initializes the project; Installs the required packages and creates the required folders.
```
make call_api [NUM_PROCESSES=4]
```
Calls the API and saves the data to the `data/parquet` folder. You can specify the number of processes to use by using the `NUM_PROCESSES` variable, default is 4. All metadata is already saved to the database due to its low volume.
```
make process_parquet
```
Runs the database container and processes the parquet files to the database.

```
make setup_models
```
Runs the database container and trains the models. These models will be saved in `backend/ml_models` for usage in the dashboard.

```
make process_all [NUM_PROCESSES=4]
```
Calls the API, processes the parquet files and saves the data to the database, factually a combination of the `call_api` and `process_parquet` commands. You can specify the number of processes to use by using the `NUM_PROCESSES` variable, default is 4.
```
make run
```
Starts the database container and runs the streamlit dashboard.
```
make test
```
Runs the tests.
```
make format
```
Formats the code using black.
```
make lint
```
Lints the code using ruff.

## Common issues
### Docker
It might be possible that when running commands that will startup the database container, such as `make process_parquet` or `make run`, you will get an error that `psycopg2` can't connect to the database. This is because the database container is not fully started yet. To fix this, run the command again. 