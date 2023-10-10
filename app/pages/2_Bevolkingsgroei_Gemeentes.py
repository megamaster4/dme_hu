import streamlit as st
import polars as pl
import altair as alt
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import crud, models
from backend.db_tools import DBEngine
from backend.config import Settings, DFType

from sqlalchemy import select

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
    return df


st.set_page_config(
    page_title="Bevolkingsgroei Gemeentes",
)

st.sidebar.header("Bevolkingsgroei per Gemeente")

st.markdown(
    """
    ## Bevolkingsgroei per Gemeente
    In dit tabblad wordt er gekeken naar de bevolkingsgroei van actieve gemeentes in Nederland. Omdat het voor kan komen dat een gemeente is opgeheven, wordt
    alleen gekeken naar gemeentes die in het jaar 2023 nog actief zijn.

    De top 5 gemeentes met de hoogste relatieve en absolute groei, van het jaar 1988 tot en met 2023, worden hieronder weergegeven.
    """
)

df = get_data_gemeentes()

devdf = df.clone()
active_gemeentes = devdf.filter(pl.col('jaar') == pl.col('jaar').max())
active_gemeentes = active_gemeentes.drop_nulls('bevolking_1_januari').select(pl.col('regio'))
devdf = devdf.filter(devdf['regio'].is_in(active_gemeentes['regio']))

devdf = devdf.with_columns((pl.col('bevolking_1_januari').shift(5)).over('regio').alias('previous_moment'))
devdf = devdf.with_columns(((pl.col('bevolking_1_januari') - pl.col('previous_moment'))/pl.col('previous_moment')*100).alias('percentage_growth'))
devdf = devdf.with_columns((pl.col('bevolking_1_januari') - pl.col('previous_moment')).alias('absolute_growth'))

relatief, absolute = st.tabs(['Top 5 Relatieve Groei', 'Top 5 Absolute Groei'])

devdf_max_year = devdf.filter(pl.col('jaar') == pl.col('jaar').max())

with relatief:
    st.markdown(
        """
        ### Top 5 Relatieve Groei
        De top 5 gemeentes met de hoogste relatieve groei in de afgelopen 5 jaar:
        """
    )
    
    df_relatief = devdf_max_year.sort('percentage_growth', descending=True).head(5)
    chart = alt.Chart(df_relatief).mark_bar().encode(
        x='percentage_growth',
        y=alt.Y('regio', sort='-x')
    ).properties(height=600, width=800)
    st.altair_chart(chart, use_container_width=True)

with absolute:
    st.markdown(
        """
        ### Top 5 Absolute Groei
        De top 5 gemeentes met de hoogste absolute groei in de afgelopen 5 jaar:
        """
    )
    df_absolute = devdf_max_year.sort('absolute_growth', descending=True).head(5)
    chart = alt.Chart(df_absolute).mark_bar().encode(
        x='absolute_growth',
        y=alt.Y('regio', sort='-x')
    ).properties(height=600, width=800)
    st.altair_chart(chart, use_container_width=True)


st.markdown(
    """
    Hoe komt het dat de gemeente Amsterdam zo'n grote groei heeft? En waarom is de gemeente Noordwijk zo'n uitschieter qua relatieve groei?

    We gaan het bodemgebruik toevoegen aan zowel de gemeente Amsterdam als Noordwijk om te kijken of we hier een verklaring voor kunnen vinden.

    ## Bodemgebruik Amsterdam en Noordwijk
    Om een goede vergelijking te kunnen geven, wordt er gekeken naar het relatieve bodemgebruik ten opzichte van het totale oppervlakte van de gemeente.
    """
)

df_bodem = get_data_gemeentes_bodemgebruik()

absolute_columns = models.Bodemgebruik.__table__.columns.keys()

relative_columns = [f"{column}_relatief" for column in absolute_columns]

devdf_bodem = df_bodem.clone()
devdf_bodem = devdf_bodem.filter((pl.col('jaar') == pl.col('jaar').max()) & (pl.col('regio').is_in(['Amsterdam', 'Noordwijk'])))
print(devdf_bodem)
