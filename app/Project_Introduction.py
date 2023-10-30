import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

st.set_page_config(
    page_title="Project Introduction",
)

st.title("Wat maakt een gemeente een fijne plek om te wonen?")

st.markdown(
    """
    ## Project Introductie
    In dit project wordt er gekeken naar de leefbaarheid van gemeentes in Nederland. Voor de scope van dit project wordt enkel gekeken naar het bevolkingsaantal,
    de burgerlijke staat, de leeftijd van de inwoners en het bodemgebruik in hectare van de gemeenten. De data is afkomstig van het CBS Statline API.

    ### Data
    De data is afkomstig van het CBS Statline API. Ter borging en ontlasting van de database, is er voor gekozen om eerst de data op te slaan in een Parquet bestand.
    Vervolgens is de data opgeslagen in een PostgreSQL database. De data is opgeslagen in verschillende tabellen. De tabellen zijn als volgt:

    #### Metadata
    - `regios`: bevat de regio's van Nederland en die worden gebruikt binnen de data
    - `perioden`: bevat de perioden van de data, in jaren, van het jaar 1988 tot en met 2023
    - `categorygroup`: bevat de leeftijdscategorieën van de leeftijd tabel
    - `geslacht`: bevat de verschillende geslachten binnen de data
    - `leeftijd`: bevat de leeftijden, in jaren, reikend van 0 tot en met 105 jaar
    - `burgstaat`: bevat de verschillende categorieën binnen de burgerlijke staat

    #### Data
    - `bevolking`: bevat de bevolkingsaantallen, bijbehorend geslacht, leeftijd en burgerlijke staat van de data
    - `bodemgebruik`: bevat het bodemgebruik van de verschillende regio's

    ### Data Analyse
    In de verschillende tabbladen wordt stilgestaand bij verschillende vraagstukken omtrent de bevolkingsgroei en leefbaarheid van de gemeentes in Nederland.
    """
)

st.sidebar.success("Selecteer een tabblad om te beginnen")

# db_engine = DBEngine(**Settings().model_dump())


# @st.cache_data
# def get_metadata():
#     df_regios = crud.select_table_from_db(db_engine=db_engine, table=models.Regios, package=DFType.POLARS)
#     regios_list = df_regios['regio'].unique().to_list()
#     return regios_list, df_regios

# regios_list, df_regios = get_metadata()

# st.title('Regios')
# st.subheader('Data from CBS Statline API')
# options_regios = st.multiselect('Select columns', regios_list)
# print(options_regios)
# options_regio_keys = df_regios.filter(df_regios['regio'].is_in(options_regios))['regio_key'].unique().to_list()
# stmt = (
#     select(models.Bevolking.bevolking_1_januari, models.Geslacht.geslacht, models.Regios.regio, models.CategoryGroup.catgroup, models.Burgstaat.burgerlijkestaat, models.Perioden.jaar)
#     .join(models.Geslacht, models.Bevolking.geslacht_key == models.Geslacht.geslacht_key)
#     .join(models.Perioden, models.Bevolking.datum_key == models.Perioden.datum_key)
#     .join(models.Regios, models.Bevolking.regio_key == models.Regios.regio_key)
#     .join(models.Leeftijd, models.Bevolking.leeftijd_key == models.Leeftijd.leeftijd_key)
#     .join(models.CategoryGroup, models.Leeftijd.categorygroupid == models.CategoryGroup.catgroup_key)
#     .join(models.Burgstaat, models.Bevolking.burgst_key == models.Burgstaat.burgst_key)
#     # .join(models.Bodemgebruik, (models.Bevolking.regio_key == models.Bodemgebruik.regio_key) & (models.Bevolking.datum_key == models.Bodemgebruik.datum_key))
#     .filter(models.Regios.regio_key.in_(options_regio_keys))
#     .where(models.CategoryGroup.catgroup == "Totaal")
#     .where(models.Burgstaat.burgerlijkestaat == "Totaal burgerlijke staat")
# )
# df = crud.fetch_data(stmt=stmt, db_engine=db_engine, package=DFType.PANDAS)

# st.bar_chart(data=df, x='jaar', y='bevolking_1_januari', color='geslacht', height=600, width=800)
