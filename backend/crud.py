import os
import sys
from typing import Union

import pandas as pd
import polars as pl

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loguru import logger
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.declarative import DeclarativeMeta

from backend.config import DFType
from backend.db_tools import DBEngine
from backend.models import (Bevolking, Bodemgebruik, Burgstaat, CategoryGroup,
                            Geslacht, Leeftijd, Perioden, Regios)


def select_from_db(db_engine: DBEngine, table: DeclarativeMeta, package: DFType = DFType.POLARS) -> pl.DataFrame:
    """Select data from database."""
    stmt = (
        select(table)
    )
    result = [query[0].__dict__ for query in db_engine.session.execute(stmt).all()]

    if package.name == 'POLARS':
        return pl.DataFrame(result, schema=table.__table__.columns.keys())
    elif package.name == 'PANDAS':
        return pd.DataFrame(result, columns=table.__table__.columns.keys())


def upsert(db_engine: DBEngine, table: DeclarativeMeta, data: list[Union[Burgstaat, Perioden, Bevolking, Bodemgebruik, Regios, CategoryGroup, Geslacht, Leeftijd]]) -> None:
    """Upsert data into database."""
    if len(data) == 0:
        logger.warning(f'No data to upsert into {table.__tablename__}.')
        return False

    data_dict = [{k: v for k, v in value.__dict__.items() if not k.startswith("_")} for value in data]

    stmt = insert(table).values(data_dict)
    stmt = stmt.on_conflict_do_update(
        index_elements=[table.__table__.primary_key.columns.values()[0]],
        set_=stmt.excluded
    )
    db_engine.session.execute(stmt)
    db_engine.session.commit()
