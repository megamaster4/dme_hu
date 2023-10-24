from pathlib import Path
import sys

import polars as pl
import streamlit as st
from sqlalchemy import select

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import crud, models
from backend.config import DFType, Settings
from backend.db_tools import DBEngine

db_engine = DBEngine(**Settings().model_dump())

@st.cache_data
def get_data():
    stmt = (
        select(models.Bevolking.bevolking_1_januari, models.Geslacht.geslacht, models.Regios.regio, models.CategoryGroup.catgroup, models.Burgstaat.burgerlijkestaat, models.Perioden.jaar)
        .join(models.Geslacht, models.Bevolking.geslacht_key == models.Geslacht.geslacht_key)
        .join(models.Perioden, models.Bevolking.datum_key == models.Perioden.datum_key)
        .join(models.Regios, models.Bevolking.regio_key == models.Regios.regio_key)
        .join(models.Leeftijd, models.Bevolking.leeftijd_key == models.Leeftijd.leeftijd_key)
        .join(models.CategoryGroup, models.Leeftijd.categorygroupid == models.CategoryGroup.catgroup_key)
        .join(models.Burgstaat, models.Bevolking.burgst_key == models.Burgstaat.burgst_key)
        # .join(models.Bodemgebruik, (models.Bevolking.regio_key == models.Bodemgebruik.regio_key) & (models.Bevolking.datum_key == models.Bodemgebruik.datum_key))
        .filter(models.Regios.regio_key == 'NL01  ')
        .filter(models.CategoryGroup.catgroup == "Totaal")
        .filter(models.Burgstaat.burgerlijkestaat == "Totaal burgerlijke staat")
    )

    df = crud.fetch_data(stmt=stmt, db_engine=db_engine, package=DFType.POLARS)
    return df

st.set_page_config(
    page_title="Bevolkingsgroei Nederland",
)

st.sidebar.header("Bevolkingsgroei in Nederland")

st.markdown(
    """
    ## Bevolkingsgroei in Nederland
    In dit tabblad wordt er gekeken naar de bevolkingsgroei in Nederland, van het jaar 1988 tot en met 2023, met een onderverdeling binnen de verschillende leeftijdscategorieën.
    """
)

df = get_data()

with st.container():
    st.markdown(
        """
        ### Jaarlijkse totale groei Nederland
        De jaarlijkse totale groei van Nederland, van het jaar 1988 tot en met 2023, is als volgt:
        """
    )
    toggle_geslacht = st.toggle('Split op geslacht', value=False)

    if toggle_geslacht:
        df_geslacht = df.filter(pl.col('geslacht') != 'Totaal mannen en vrouwen')
        st.bar_chart(data=df_geslacht.to_pandas(), x='jaar', y='bevolking_1_januari', color='geslacht', height=600, width=800)
    else:
        df_geslacht = df.filter(pl.col('geslacht') == 'Totaal mannen en vrouwen')
        st.bar_chart(data=df_geslacht.to_pandas(), x='jaar', y='bevolking_1_januari', height=600, width=800)

with st.container():
    st.markdown(
        """
        ### Relatieve groei Nederland
        De relatieve groei van Nederland, van het jaar 1988 tot en met 2023, is als volgt:
        """
    )
    radio_rel_abs = st.radio(
        "Relatieve of absolute groei?",
        ('Relatief', 'Absoluut'),
        label_visibility='hidden'
    )

    df_growth = df.filter(pl.col('geslacht') == 'Totaal mannen en vrouwen')
    df_growth = df_growth.with_columns((pl.col('bevolking_1_januari').shift(1)).over('regio').alias('previous_year'))
    df_growth = df_growth.with_columns(((pl.col('bevolking_1_januari') - pl.col('previous_year'))/pl.col('previous_year')*100).alias('relative_growth'))
    df_growth = df_growth.with_columns((pl.col('bevolking_1_januari') - pl.col('previous_year')).alias('absolute_growth'))
    
    if radio_rel_abs == 'Relatief':
        st.line_chart(data=df_growth.to_pandas(), x='jaar', y='relative_growth', height=600, width=800)
    elif radio_rel_abs == 'Absoluut':
        st.line_chart(data=df_growth.to_pandas(), x='jaar', y='absolute_growth', height=600, width=800)
    
