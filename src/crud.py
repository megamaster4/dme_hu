from loguru import logger
from typing import Union
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.declarative import DeclarativeMeta

from src.db_tools import DBEngine
from src.models import Burgstaat, Perioden, Bevolking, Regios, CategoryGroup, Geslacht, Leeftijd


def upsert(db_engine: DBEngine, table: DeclarativeMeta, data: list[Union[Burgstaat, Perioden, Bevolking, Regios, CategoryGroup, Geslacht, Leeftijd]]) -> None:
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


def get_burgstaat(db_engine: DBEngine) -> list[Burgstaat]:
    """Get all Burgstaat records from database."""
    stmt = (
        select(
            Burgstaat
        )
    )
    return [row[0] for row in db_engine.session.execute(stmt).all()]
