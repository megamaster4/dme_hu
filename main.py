from pathlib import Path
from loguru import logger
from tqdm import tqdm

from backend.utils import parse_parquet_to_db, get_data_from_cbs, get_metadata_from_cbs
from backend.db_tools import DBEngine
from backend.config import Settings
from backend.models import Bevolking, Bodemgebruik, Regios
from backend.crud import select_from_db


def main():
    # Connect to database and create engine
    db_engine = DBEngine(**Settings().model_dump())

    # Get metadata from CBS Statline API and upsert into database
    get_metadata_from_cbs(db_engine=db_engine)

    # Get data from CBS Statline API and save as parquet files
    get_data_from_cbs(object=Bevolking, url="https://opendata.cbs.nl/ODataFeed/odata/03759ned/TypedDataSet", num_processes=4)
    get_data_from_cbs(object=Bodemgebruik, url="https://opendata.cbs.nl/ODataFeed/odata/70262ned/TypedDataSet", num_processes=6)

    # Get regio keys from database
    regios = select_from_db(db_engine=db_engine, table=Regios)
    regio_keys = regios['regio_key'].unique()

    # Parse parquet files and upsert into database
    folders = {Bevolking: Path("data/parquet/bevolking"), Bodemgebruik: Path("data/parquet/bodemgebruik")}
    for object, folder in folders.items():
        parquetFiles = folder.rglob('*.parquet')
        nrows = len(list(parquetFiles))
        logger.info(f"Found {nrows} parquet files in {folder}.")
        for file in tqdm(folder.iterdir(), total=nrows):
            if file.suffix == ".parquet":
                parse_parquet_to_db(path=file, object=object, db_engine=db_engine, regios=regio_keys)


if __name__ == "__main__":
    main()
