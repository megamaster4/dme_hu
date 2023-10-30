from pathlib import Path

import click
from loguru import logger
from tqdm import tqdm

from backend.config import Settings
from backend.crud import select_table_from_db
from backend.db_tools import DBEngine
from backend.models import Bevolking, Bodemgebruik, Regios
from backend.utils import get_data_from_cbs, get_metadata_from_cbs, parse_parquet_to_db


@click.command()
@click.option(
    "--callapi", is_flag=True, help="Call CBS Statline API to get metadata and data."
)
@click.option(
    "--num-processes",
    default=4,
    help="Number of processes to use for downloading data from CBS Statline API.",
)
@click.option(
    "--process-parquet",
    default="",
    help="Path to folder with parquet files to process and upsert into database.",
)
def main(callapi: bool, num_processes: int, process_parquet: str, dashboard: bool):
    # Connect to database and create engine
    db_engine = DBEngine(**Settings().model_dump())

    if callapi:
        # Get metadata from CBS Statline API and upsert into database
        get_metadata_from_cbs(db_engine=db_engine)
        # Get data from CBS Statline API and save as parquet files
        get_data_from_cbs(
            object=Bevolking,
            url="https://opendata.cbs.nl/ODataFeed/odata/03759ned/TypedDataSet",
            num_processes=num_processes,
        )
        get_data_from_cbs(
            object=Bodemgebruik,
            url="https://opendata.cbs.nl/ODataFeed/odata/70262ned/TypedDataSet",
            num_processes=num_processes,
        )

    if process_parquet != "":
        # Get regio keys from database
        regios = select_table_from_db(db_engine=db_engine, table=Regios)
        regio_keys = regios["regio_key"].unique()

        # Parse parquet files and upsert into database
        folders = {
            Bevolking: Path(f"{process_parquet}/bevolking"),
            Bodemgebruik: Path(f"{process_parquet}/bodemgebruik"),
        }
        for object, folder in folders.items():
            parquetFiles = folder.rglob("*.parquet")
            nrows = len(list(parquetFiles))
            logger.info(f"Found {nrows} parquet files in {folder}.")
            for file in tqdm(folder.iterdir(), total=nrows):
                if file.suffix == ".parquet":
                    parse_parquet_to_db(
                        path=file, object=object, db_engine=db_engine, regios=regio_keys
                    )

if __name__ == "__main__":
    main()
