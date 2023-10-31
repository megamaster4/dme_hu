# Instructions
To run the program, use the makefile commands. The makefile is located in the root folder. 

## Usage
The makefile abstract certain commands for ease of use. The following commands are available, described below but also under the `help` command;
- `help`
    -  Displays the help menu
- `init`
    -  Initializes the project; Installs the required packages, creates the database container and creates the required folders.
- `call_api [NUM_PROCESSES=4]`
    -  Calls the API and saves the data to the `data/parquet` folder. You can specify the number of processes to use by using the `NUM_PROCESSES` variable, default is 4.
- `process_parquet`
    -  Runs the database container and processes the parquet files to the database.
- `process_all [NUM_PROCESSES=4]`
    -  Calls the API, processes the parquet files and saves the data to the database, factually a combination of the `call_api` and `process_parquet` commands. You can specify the number of processes to use by using the `NUM_PROCESSES` variable, default is 4.
- `run`
    -  Starts the database container and runs the streamlit dashboard.
- `test`
    -  Runs the tests.
- `format`
    -  Formats the code using black.
- `lint`
    -  Lints the code using ruff.