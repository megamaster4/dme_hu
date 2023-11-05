import sys
from pathlib import Path
from typing import Union

import pandas as pd
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.declarative import DeclarativeMeta

from backend.config import DFType
from backend.db_tools import DBEngine
from backend.models import (
    Bevolking,
    Bodemgebruik,
    Burgstaat,
    CategoryGroup,
    Geslacht,
    Leeftijd,
    Perioden,
    Regios,
)


def fetch_data(
    stmt: select, db_engine: DBEngine, package: DFType = DFType.POLARS
) -> Union[pl.DataFrame, pd.DataFrame]:
    compiled_stmt = stmt.compile(
        bind=db_engine.engine, compile_kwargs={"literal_binds": True}
    ).string

    if package.name == "POLARS":
        result_df = pl.read_database(query=compiled_stmt, connection=db_engine.engine)
    elif package.name == "PANDAS":
        result_df = pd.read_sql(sql=compiled_stmt, con=db_engine.engine)
    return result_df


def select_table_from_db(
    db_engine: DBEngine, table: DeclarativeMeta, package: DFType = DFType.POLARS
) -> pl.DataFrame:
    """Select data from database."""
    stmt = select(table)
    result = [query[0].__dict__ for query in db_engine.session.execute(stmt).all()]

    if package.name == "POLARS":
        return pl.DataFrame(result, schema=table.__table__.columns.keys())
    elif package.name == "PANDAS":
        return pd.DataFrame(result, columns=table.__table__.columns.keys())


def upsert(
    db_engine: DBEngine,
    table: DeclarativeMeta,
    data: list[
        Union[
            Burgstaat,
            Perioden,
            Bevolking,
            Bodemgebruik,
            Regios,
            CategoryGroup,
            Geslacht,
            Leeftijd,
        ]
    ],
) -> None:
    """Upsert data into database."""
    if len(data) == 0:
        logger.warning(f"No data to upsert into {table.__tablename__}.")
        return False

    data_dict = [
        {k: v for k, v in value.__dict__.items() if not k.startswith("_")}
        for value in data
    ]

    stmt = insert(table).values(data_dict)
    stmt = stmt.on_conflict_do_update(
        index_elements=[table.__table__.primary_key.columns.values()[0]],
        set_=stmt.excluded,
    )
    db_engine.session.execute(stmt)
    db_engine.session.commit()


def get_bevolking_landelijk(_db_engine: DBEngine):
    stmt = (
        select(
            Bevolking.bevolking_1_januari,
            Geslacht.geslacht,
            Regios.regio,
            CategoryGroup.catgroup,
            Burgstaat.burgerlijkestaat,
            Perioden.jaar,
        )
        .join(
            Geslacht,
            Bevolking.geslacht_key == Geslacht.geslacht_key,
        )
        .join(Perioden, Bevolking.datum_key == Perioden.datum_key)
        .join(Regios, Bevolking.regio_key == Regios.regio_key)
        .join(
            Leeftijd,
            Bevolking.leeftijd_key == Leeftijd.leeftijd_key,
        )
        .join(
            CategoryGroup,
            Leeftijd.categorygroupid == CategoryGroup.catgroup_key,
        )
        .join(Burgstaat, Bevolking.burgst_key == Burgstaat.burgst_key)
        .filter(Regios.regio_key == "NL01  ")
        .filter(CategoryGroup.catgroup == "Totaal")
        .filter(Burgstaat.burgerlijkestaat == "Totaal burgerlijke staat")
    )

    df = fetch_data(stmt=stmt, db_engine=_db_engine, package=DFType.POLARS)
    return df


def get_bodemgebruik_landelijk(_db_engine: DBEngine):
    stmt = (
        select(
            Bevolking.bevolking_1_januari,
            Geslacht.geslacht,
            Regios.regio,
            CategoryGroup.catgroup,
            Burgstaat.burgerlijkestaat,
            Perioden.jaar,
            Bodemgebruik,
        )
        .join(
            Geslacht,
            Bevolking.geslacht_key == Geslacht.geslacht_key,
        )
        .join(Perioden, Bevolking.datum_key == Perioden.datum_key)
        .join(Regios, Bevolking.regio_key == Regios.regio_key)
        .join(
            Leeftijd,
            Bevolking.leeftijd_key == Leeftijd.leeftijd_key,
        )
        .join(
            CategoryGroup,
            Leeftijd.categorygroupid == CategoryGroup.catgroup_key,
        )
        .join(Burgstaat, Bevolking.burgst_key == Burgstaat.burgst_key)
        .join(
            Bodemgebruik,
            (Bevolking.regio_key == Bodemgebruik.regio_key)
            & (Bevolking.datum_key == Bodemgebruik.datum_key),
        )
        .filter(Regios.regio_key == "NL01  ")
        .filter(CategoryGroup.catgroup == "Totaal")
        .filter(Burgstaat.burgerlijkestaat == "Totaal burgerlijke staat")
    )

    df = fetch_data(stmt=stmt, db_engine=_db_engine, package=DFType.POLARS)
    df = df.drop(["id", "regio_key", "datum_key"])
    return df


def get_data_gemeentes(_db_engine: DBEngine):
    stmt = (
        select(
            Bevolking.bevolking_1_januari,
            Geslacht.geslacht,
            Regios.regio,
            CategoryGroup.catgroup,
            Burgstaat.burgerlijkestaat,
            Perioden.jaar,
        )
        .join(
            Geslacht,
            Bevolking.geslacht_key == Geslacht.geslacht_key,
        )
        .join(Perioden, Bevolking.datum_key == Perioden.datum_key)
        .join(Regios, Bevolking.regio_key == Regios.regio_key)
        .join(
            Leeftijd,
            Bevolking.leeftijd_key == Leeftijd.leeftijd_key,
        )
        .join(
            CategoryGroup,
            Leeftijd.categorygroupid == CategoryGroup.catgroup_key,
        )
        .join(Burgstaat, Bevolking.burgst_key == Burgstaat.burgst_key)
        .filter(Regios.regio_key.startswith("GM"))
        .filter(CategoryGroup.catgroup == "Totaal")
        .filter(Burgstaat.burgerlijkestaat == "Totaal burgerlijke staat")
        .filter(Geslacht.geslacht == "Totaal mannen en vrouwen")
    )

    df = fetch_data(stmt=stmt, db_engine=_db_engine, package=DFType.POLARS)
    return df


def get_data_gemeentes_bodemgebruik(_db_engine: DBEngine):
    stmt = (
        select(
            Bevolking.bevolking_1_januari,
            Geslacht.geslacht,
            Regios.regio,
            CategoryGroup.catgroup,
            Burgstaat.burgerlijkestaat,
            Perioden.jaar,
            Bodemgebruik,
        )
        .join(
            Geslacht,
            Bevolking.geslacht_key == Geslacht.geslacht_key,
        )
        .join(Perioden, Bevolking.datum_key == Perioden.datum_key)
        .join(Regios, Bevolking.regio_key == Regios.regio_key)
        .join(
            Leeftijd,
            Bevolking.leeftijd_key == Leeftijd.leeftijd_key,
        )
        .join(
            CategoryGroup,
            Leeftijd.categorygroupid == CategoryGroup.catgroup_key,
        )
        .join(Burgstaat, Bevolking.burgst_key == Burgstaat.burgst_key)
        .join(
            Bodemgebruik,
            (Bevolking.regio_key == Bodemgebruik.regio_key)
            & (Bevolking.datum_key == Bodemgebruik.datum_key),
        )
        .filter(Regios.regio_key.startswith("GM"))
        .filter(CategoryGroup.catgroup == "Totaal")
        .filter(Burgstaat.burgerlijkestaat == "Totaal burgerlijke staat")
        .filter(Geslacht.geslacht == "Totaal mannen en vrouwen")
    )

    df = fetch_data(stmt=stmt, db_engine=_db_engine, package=DFType.POLARS)
    df = df.drop(["id", "regio_key", "datum_key"])
    return df
