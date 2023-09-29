import streamlit as st
from pathlib import Path
from loguru import logger
from tqdm import tqdm

from utils import get_metadata_from_cbs, get_data_from_cbs, parse_parquet_to_db
from db_tools import DBEngine
from config import Settings
from models import Bevolking, Bodemgebruik

def main():
    # Connect to database and create engine
    # db_engine = DBEngine(**Settings().model_dump())
    
    # Get metadata from CBS Statline API and upsert into database
    # get_metadata_from_cbs(db_engine=db_engine)

    # Get data from CBS Statline API and save as parquet files
    # get_data_from_cbs(object=Bevolking, url="https://opendata.cbs.nl/ODataFeed/odata/03759ned/TypedDataSet", num_processes=4)
    get_data_from_cbs(object=Bodemgebruik, url="https://opendata.cbs.nl/ODataFeed/odata/70262ned/TypedDataSet", num_processes=6)


    # Parse parquet files and upsert into database
    # folder = Path("data/parquet/bevolking")
    # for file in folder.iterdir():
    #     if file.suffix == ".parquet":
    #         parse_parquet_to_db(path=file, object=Bevolking, db_engine=db_engine)





    # parse_parquet_to_db(path="data/parquet/bevolking/Bevolking_10000.parquet", object=Bevolking, db_engine=db_engine)

    # st.title('Leeftijd')
    # st.subheader('Data from CBS Statline API')
    # options = st.multiselect('Select columns', df['leeftijd'].unique())
    # st.write(df.loc[df['leeftijd'].isin(options)])

    # logger.info(df)


if __name__ == "__main__":
    main()
    
