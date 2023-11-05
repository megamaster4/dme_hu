from pathlib import Path
import sys

import polars as pl
import streamlit as st
from joblib import load
from sklearn.metrics import mean_squared_error, r2_score

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import Settings
from backend.db_tools import DBEngine


@st.cache_resource
def connect_db() -> DBEngine:
    """Connect to database."""
    db_engine = DBEngine(**Settings().model_dump())
    return db_engine


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


def load_models(model_names: list[str]) -> dict[str, object]:
    loaded_models = {k: load(f"backend/ml_models/{k}.joblib") for k in model_names}
    return loaded_models


def model_metrics(
    X_test: pl.DataFrame, y_test: pl.Series, model: object
) -> tuple[float, float]:
    y_pred = model.predict(X_test)
    MSE = mean_squared_error(y_test, y_pred)
    R2 = r2_score(y_test, y_pred)
    return MSE, R2
