import streamlit as st

from loguru import logger

from models import Burgstaat, CategoryGroup, Geslacht, Leeftijd, Perioden, Regios
from utils import parse_response, parse_response_bevolking
from crud import select_polars, upsert
from db_tools import DBEngine
from config import Settings


def get_data_from_cbs(db_engine: DBEngine) -> None:
    # Get data from CBS Statline API and upsert into database
    data_dict = {
        "BurgerlijkeStaat": Burgstaat,
        "CategoryGroups": CategoryGroup,
        "Geslacht": Geslacht,
        "Leeftijd": Leeftijd,
        "Perioden": Perioden,
        "RegioS": Regios,
    }

    for key, value in data_dict.items():
        logger.info(f"Getting data from {key}...")
        data = parse_response(
            url=f"https://opendata.cbs.nl/ODataFeed/odata/03759ned/{key}", object=value
        )
        upsert(db_engine=db_engine, table=value, data=data)
        logger.info(f"Upserted {len(data)} records into {key}.")

    # Get Bevolking data from CBS Statline API and upsert into database
    logger.info("Getting data from Bevolking...")
    data, rows = parse_response_bevolking(direct_upsert=True, db_engine=db_engine)
    logger.info(f"Parsed and inserted {rows} rows.")

    logger.info("Done!")


def main():
    # Connect to database and create engine
    db_engine = DBEngine(**Settings().model_dump())

    get_data_from_cbs(db_engine=db_engine)
    # df = select_polars(db_engine=db_engine, table=Leeftijd)

    # st.title('Leeftijd')
    # st.subheader('Data from CBS Statline API')
    # options = st.multiselect('Select columns', df['leeftijd'].unique())
    # st.write(df.loc[df['leeftijd'].isin(options)])

    # logger.info(df)


if __name__ == "__main__":
    main()
