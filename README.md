# Instructions
To run the program, use the makefile commands. The makefile is located in the root folder. The following commands are available;

## Usage
Call CBS Statline API to get metadata and data. The data is stored in a parquet file, located in `data/parquet` folder.
Use the `--num-processes` flag to specify the number of processes to use for the API calls. The default is 4.

```bash
python main.py --callapi --num-processes
```

Process the parquet files to the local postgresql database, which are located in the `data/parquet` folder.

```bash
python main.py --process-parquet
```

Run and open the dashboard in the browser. The dashboard is located at `http://localhost:8050/`.

```bash
python main.py --dashboard
```

## Postgresql Database
This project uses a local postgresql database to store the processed data, which is hosted in a docker container. The docker-compose file is located in the `docker` folder. To run the database, use the following command;

```bash
docker-compose up -d
```

The database is created using the `db_init.sql` file, which is located in the `data/sql` folder.
