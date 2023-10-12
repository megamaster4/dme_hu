import os
import sys

import altair as alt
import polars as pl
import streamlit as st
from sqlalchemy import select

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import crud, models
from backend.config import DFType, Settings
from backend.db_tools import DBEngine

db_engine = DBEngine(**Settings().model_dump())


@st.cache_data
def get_data_gemeentes():
    """get_data_gemeentes _summary_

    Returns:
        _type_: _description_
    """
    stmt = (
        select(models.Bevolking.bevolking_1_januari, models.Geslacht.geslacht, models.Regios.regio, models.CategoryGroup.catgroup, models.Burgstaat.burgerlijkestaat, models.Perioden.jaar)
        .join(models.Geslacht, models.Bevolking.geslacht_key == models.Geslacht.geslacht_key)
        .join(models.Perioden, models.Bevolking.datum_key == models.Perioden.datum_key)
        .join(models.Regios, models.Bevolking.regio_key == models.Regios.regio_key)
        .join(models.Leeftijd, models.Bevolking.leeftijd_key == models.Leeftijd.leeftijd_key)
        .join(models.CategoryGroup, models.Leeftijd.categorygroupid == models.CategoryGroup.catgroup_key)
        .join(models.Burgstaat, models.Bevolking.burgst_key == models.Burgstaat.burgst_key)
        .filter(models.Regios.regio_key.startswith('GM'))
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
        select(models.Bevolking.bevolking_1_januari, models.Geslacht.geslacht, models.Regios.regio, models.CategoryGroup.catgroup, models.Burgstaat.burgerlijkestaat, models.Perioden.jaar, models.Bodemgebruik)
        .join(models.Geslacht, models.Bevolking.geslacht_key == models.Geslacht.geslacht_key)
        .join(models.Perioden, models.Bevolking.datum_key == models.Perioden.datum_key)
        .join(models.Regios, models.Bevolking.regio_key == models.Regios.regio_key)
        .join(models.Leeftijd, models.Bevolking.leeftijd_key == models.Leeftijd.leeftijd_key)
        .join(models.CategoryGroup, models.Leeftijd.categorygroupid == models.CategoryGroup.catgroup_key)
        .join(models.Burgstaat, models.Bevolking.burgst_key == models.Burgstaat.burgst_key)
        .join(models.Bodemgebruik, (models.Bevolking.regio_key == models.Bodemgebruik.regio_key) & (models.Bevolking.datum_key == models.Bodemgebruik.datum_key))
        .filter(models.Regios.regio_key.startswith('GM'))
        .filter(models.CategoryGroup.catgroup == "Totaal")
        .filter(models.Burgstaat.burgerlijkestaat == "Totaal burgerlijke staat")
        .filter(models.Geslacht.geslacht == "Totaal mannen en vrouwen")
    )

    df = crud.fetch_data(stmt=stmt, db_engine=db_engine, package=DFType.POLARS)
    df = df.drop(['id', 'regio_key', 'datum_key'])
    return df


def extract_top5(df: pl.DataFrame, only_active: bool = True) -> pl.DataFrame:
    if only_active:
        active_gemeentes = df.filter(pl.col('jaar') == pl.col('jaar').max())
        active_gemeentes = active_gemeentes.drop_nulls('bevolking_1_januari').select(pl.col('regio'))
        df = df.filter(df['regio'].is_in(active_gemeentes['regio']))

    df = df.with_columns((pl.col('bevolking_1_januari').shift(5)).over('regio').alias('previous_moment'))
    df = df.with_columns(((pl.col('bevolking_1_januari') - pl.col('previous_moment'))/pl.col('previous_moment')).alias('percentage_growth'))
    df = df.with_columns((pl.col('bevolking_1_januari') - pl.col('previous_moment')).alias('absolute_growth'))
    return df


def growth_columns_by_year(df: pl.DataFrame, columns_to_exclude: list[str]) -> pl.DataFrame:
    use_cols = [col for col in df.columns if col not in columns_to_exclude]

    for column in use_cols:
        df = df.with_columns((pl.col(column).shift(1)).over('regio').alias(f'{column}_previous_moment'))
        df = df.with_columns(((pl.col(column) - pl.col(f'{column}_previous_moment'))/pl.col(f'{column}_previous_moment')).alias(f'{column}_growth'))
        df = df.fill_nan(0)

    return df


def divide_columns_by_column(df: pl.DataFrame, divide_by_column: str, columns_to_exclude: list[str]) -> pl.DataFrame:
    # Get a list of column names except the list to exclude
    columns_to_exclude.append(divide_by_column)
    columns_to_divide = [col for col in df.columns if col not in columns_to_exclude]

    # Iterate through the columns and divide by the specified column
    for column in columns_to_divide:
        df = df.with_columns((df[column] / df[divide_by_column]).alias(f'{column}_relative'))

    return df


def main():
    st.set_page_config(
        page_title="Bevolkingsgroei vs Bodemgebruik",
    )
    df_bevolking = get_data_gemeentes()
    df_bodem = get_data_gemeentes_bodemgebruik()
    devdf_bevolking = df_bevolking.clone()  
    devdf_bodem = df_bodem.clone()
    

    st.sidebar.header("Bevolkingsgroei vs Bodemgebruik")
    st.markdown(
        """
        ## Bevolkingsgroei per Gemeente
        In dit tabblad wordt er gekeken naar de bevolkingsgroei van actieve gemeentes in Nederland. Omdat het voor kan komen dat een gemeente is opgeheven, wordt
        alleen gekeken naar gemeentes die in het jaar 2023 nog actief zijn.

        De top 5 gemeentes met de hoogste relatieve en absolute groei, van het jaar 1988 tot en met 2023, worden hieronder weergegeven.
        """
    )

    # devdf_bevolking = extract_top5(df=devdf_bevolking, only_active=True)
    # devdf_bevolking = devdf_bevolking.filter(pl.col('jaar') == pl.col('jaar').max()).sort('percentage_growth', descending=True).head(5)

    regios = devdf_bevolking['regio'].to_list()
    exclude_cols=['regio', 'jaar', 'geslacht', 'catgroup', 'burgerlijkestaat']
    devdf_bodem = df_bodem.filter(df_bodem['regio'].is_in(regios))
    devdf_bodem = devdf_bodem.fill_null(strategy='zero')
    devdf_bodem = growth_columns_by_year(df=devdf_bodem, columns_to_exclude=exclude_cols)
    devdf_bodem = devdf_bodem[[s.name for s in devdf_bodem if not (s.null_count() == devdf_bodem.height)]]
    devdf_bodem = devdf_bodem.drop_nulls('bevolking_1_januari_growth')
    st.dataframe(devdf_bodem.to_pandas())

    devdf_bodem = devdf_bodem.select([col for col in devdf_bodem.columns if (col in exclude_cols) or (col.endswith('growth'))])
    # plot_cols = [col for col in devdf_bodem.columns if (col.endswith('growth'))]
    st.dataframe(devdf_bodem.to_pandas())
    use_cols = [col for col in devdf_bodem.columns if col not in exclude_cols]
    #average growth per year
    # devdf_bodem = devdf_bodem.group_by('jaar').mean().sort('jaar')

    # Calculate the correlation matrix
    correlation_matrix = devdf_bodem.select(use_cols).corr().with_columns(index=pl.lit(use_cols)).melt(id_vars=['index']).filter((pl.col('index') != pl.col('variable')))
    correlation_matrix = correlation_matrix.filter(pl.col('variable') == 'bevolking_1_januari_growth')
    st.dataframe(correlation_matrix.to_pandas())
    # Create a heatmap for the correlation matrix using Altair
    heatmap = alt.Chart(correlation_matrix).mark_rect().encode(
        x='variable:O',
        y='index:O',
        color=alt.Color('value:Q', scale=alt.Scale(scheme='redblue'))
    ).properties(
        height=800,
        width=800
    )
    st.altair_chart(heatmap)
        # print(devdf_bodem)

    # st.line_chart(data=devdf_bodem.to_pandas(), x='jaar', y='bevolking_1_januari_growth', color='regio', height=600, width=800)



if __name__ == "__main__":
    main()