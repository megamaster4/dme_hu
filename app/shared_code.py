from pathlib import Path
import sys

import polars as pl
import numpy as np
import streamlit as st
from sqlalchemy import select

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import crud, models
from backend.config import DFType, Settings
from backend.db_tools import DBEngine

db_engine = DBEngine(**Settings().model_dump())


@st.cache_data
def get_bevolking_landelijk():
    stmt = (
        select(
            models.Bevolking.bevolking_1_januari,
            models.Geslacht.geslacht,
            models.Regios.regio,
            models.CategoryGroup.catgroup,
            models.Burgstaat.burgerlijkestaat,
            models.Perioden.jaar,
        )
        .join(
            models.Geslacht,
            models.Bevolking.geslacht_key == models.Geslacht.geslacht_key,
        )
        .join(models.Perioden, models.Bevolking.datum_key == models.Perioden.datum_key)
        .join(models.Regios, models.Bevolking.regio_key == models.Regios.regio_key)
        .join(
            models.Leeftijd,
            models.Bevolking.leeftijd_key == models.Leeftijd.leeftijd_key,
        )
        .join(
            models.CategoryGroup,
            models.Leeftijd.categorygroupid == models.CategoryGroup.catgroup_key,
        )
        .join(
            models.Burgstaat, models.Bevolking.burgst_key == models.Burgstaat.burgst_key
        )
        .filter(models.Regios.regio_key == "NL01  ")
        .filter(models.CategoryGroup.catgroup == "Totaal")
        .filter(models.Burgstaat.burgerlijkestaat == "Totaal burgerlijke staat")
    )

    df = crud.fetch_data(stmt=stmt, db_engine=db_engine, package=DFType.POLARS)
    return df


@st.cache_data
def get_bodemgebruik_landelijk():
    """get_data_gemeentes_bodemgebruik _summary_

    Returns:
        _type_: _description_
    """
    stmt = (
        select(
            models.Bevolking.bevolking_1_januari,
            models.Geslacht.geslacht,
            models.Regios.regio,
            models.CategoryGroup.catgroup,
            models.Burgstaat.burgerlijkestaat,
            models.Perioden.jaar,
            models.Bodemgebruik,
        )
        .join(
            models.Geslacht,
            models.Bevolking.geslacht_key == models.Geslacht.geslacht_key,
        )
        .join(models.Perioden, models.Bevolking.datum_key == models.Perioden.datum_key)
        .join(models.Regios, models.Bevolking.regio_key == models.Regios.regio_key)
        .join(
            models.Leeftijd,
            models.Bevolking.leeftijd_key == models.Leeftijd.leeftijd_key,
        )
        .join(
            models.CategoryGroup,
            models.Leeftijd.categorygroupid == models.CategoryGroup.catgroup_key,
        )
        .join(
            models.Burgstaat, models.Bevolking.burgst_key == models.Burgstaat.burgst_key
        )
        .join(
            models.Bodemgebruik,
            (models.Bevolking.regio_key == models.Bodemgebruik.regio_key)
            & (models.Bevolking.datum_key == models.Bodemgebruik.datum_key),
        )
        .filter(models.Regios.regio_key == "NL01  ")
        .filter(models.CategoryGroup.catgroup == "Totaal")
        .filter(models.Burgstaat.burgerlijkestaat == "Totaal burgerlijke staat")
    )

    df = crud.fetch_data(stmt=stmt, db_engine=db_engine, package=DFType.POLARS)
    df = df.drop(["id", "regio_key", "datum_key"])
    return df


@st.cache_data
def get_data_gemeentes():
    """get_data_gemeentes _summary_

    Returns:
        _type_: _description_
    """
    stmt = (
        select(
            models.Bevolking.bevolking_1_januari,
            models.Geslacht.geslacht,
            models.Regios.regio,
            models.CategoryGroup.catgroup,
            models.Burgstaat.burgerlijkestaat,
            models.Perioden.jaar,
        )
        .join(
            models.Geslacht,
            models.Bevolking.geslacht_key == models.Geslacht.geslacht_key,
        )
        .join(models.Perioden, models.Bevolking.datum_key == models.Perioden.datum_key)
        .join(models.Regios, models.Bevolking.regio_key == models.Regios.regio_key)
        .join(
            models.Leeftijd,
            models.Bevolking.leeftijd_key == models.Leeftijd.leeftijd_key,
        )
        .join(
            models.CategoryGroup,
            models.Leeftijd.categorygroupid == models.CategoryGroup.catgroup_key,
        )
        .join(
            models.Burgstaat, models.Bevolking.burgst_key == models.Burgstaat.burgst_key
        )
        .filter(models.Regios.regio_key.startswith("GM"))
        .filter(models.CategoryGroup.catgroup == "Totaal")
        .filter(models.Burgstaat.burgerlijkestaat == "Totaal burgerlijke staat")
        .filter(models.Geslacht.geslacht == "Totaal mannen en vrouwen")
    )

    df = crud.fetch_data(stmt=stmt, db_engine=db_engine, package=DFType.POLARS)
    return df


@st.cache_data
def get_data_gemeentes_bodemgebruik():
    """get_data_gemeentes_bodemgebruik _summary_

    Returns:
        _type_: _description_
    """
    stmt = (
        select(
            models.Bevolking.bevolking_1_januari,
            models.Geslacht.geslacht,
            models.Regios.regio,
            models.CategoryGroup.catgroup,
            models.Burgstaat.burgerlijkestaat,
            models.Perioden.jaar,
            models.Bodemgebruik,
        )
        .join(
            models.Geslacht,
            models.Bevolking.geslacht_key == models.Geslacht.geslacht_key,
        )
        .join(models.Perioden, models.Bevolking.datum_key == models.Perioden.datum_key)
        .join(models.Regios, models.Bevolking.regio_key == models.Regios.regio_key)
        .join(
            models.Leeftijd,
            models.Bevolking.leeftijd_key == models.Leeftijd.leeftijd_key,
        )
        .join(
            models.CategoryGroup,
            models.Leeftijd.categorygroupid == models.CategoryGroup.catgroup_key,
        )
        .join(
            models.Burgstaat, models.Bevolking.burgst_key == models.Burgstaat.burgst_key
        )
        .join(
            models.Bodemgebruik,
            (models.Bevolking.regio_key == models.Bodemgebruik.regio_key)
            & (models.Bevolking.datum_key == models.Bodemgebruik.datum_key),
        )
        .filter(models.Regios.regio_key.startswith("GM"))
        .filter(models.CategoryGroup.catgroup == "Totaal")
        .filter(models.Burgstaat.burgerlijkestaat == "Totaal burgerlijke staat")
        .filter(models.Geslacht.geslacht == "Totaal mannen en vrouwen")
    )

    df = crud.fetch_data(stmt=stmt, db_engine=db_engine, package=DFType.POLARS)
    df = df.drop(["id", "regio_key", "datum_key"])
    return df


def divide_columns_by_column(
    df: pl.DataFrame, divide_by_column: str, columns_to_exclude: list[str]
) -> pl.DataFrame:
    # Get a list of column names except the list to exclude
    columns_to_exclude.append(divide_by_column)
    columns_to_divide = [col for col in df.columns if col not in columns_to_exclude]

    # Iterate through the columns and divide by the specified column
    for column in columns_to_divide:
        df = df.with_columns(
            (df[column] / df[divide_by_column]).alias(f"{column}_relative")
        )

    return df


def extract_top5(df: pl.DataFrame, only_active: bool = True) -> pl.DataFrame:
    if only_active:
        active_gemeentes = df.filter(pl.col("jaar") == pl.col("jaar").max())
        active_gemeentes = active_gemeentes.drop_nulls("bevolking_1_januari").select(
            pl.col("regio")
        )
        df = df.filter(df["regio"].is_in(active_gemeentes["regio"]))

    df = df.with_columns(
        (pl.col("bevolking_1_januari").shift(5)).over("regio").alias("previous_moment")
    )
    df = df.with_columns(
        (
            (pl.col("bevolking_1_januari") - pl.col("previous_moment"))
            / pl.col("previous_moment")
        ).alias("percentage_growth")
    )
    df = df.with_columns(
        (pl.col("bevolking_1_januari") - pl.col("previous_moment")).alias(
            "absolute_growth"
        )
    )
    return df


def growth_columns_by_year(
    df: pl.DataFrame, columns_to_exclude: list[str]
) -> pl.DataFrame:
    use_cols = [col for col in df.columns if col not in columns_to_exclude]

    for column in use_cols:
        df = df.with_columns(
            (pl.col(column).shift(1)).over("regio").alias(f"{column}_previous_moment")
        )
        df = df.with_columns(
            (
                (pl.col(column) - pl.col(f"{column}_previous_moment"))
                / pl.col(f"{column}_previous_moment")
            ).alias(f"{column}_growth")
        )
        df = df.fill_nan(0)

    # The following code is needed to replace inf values with 0, because of a bug in Polars.
    # We will replace them using pandas, and convert the dataframe back to polars before returning the dataframe
    df_pd = df.to_pandas()
    df_pd.replace([np.inf, -np.inf], 0, inplace=True)
    df = pl.from_pandas(df_pd)
    return df
