import streamlit as st

from backend.crud import select_from_db
from backend.db_tools import DBEngine
from backend.config import Settings, DFType
from backend.models import Leeftijd

db_engine = DBEngine(**Settings().model_dump())

df = select_from_db(db_engine=db_engine, table=Leeftijd, package=DFType.PANDAS)

st.title('Leeftijd')
st.subheader('Data from CBS Statline API')
options = st.multiselect('Select columns', df['leeftijd'].unique())
st.write(df.loc[df['leeftijd'].isin(options)])
