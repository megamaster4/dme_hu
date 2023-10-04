import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import crud
from backend.db_tools import DBEngine
from backend.config import Settings, DFType
from backend.models import Leeftijd

db_engine = DBEngine(**Settings().model_dump())

df = crud.select_from_db(db_engine=db_engine, table=Leeftijd, package=DFType.PANDAS)

st.title('Leeftijd')
st.subheader('Data from CBS Statline API')
options = st.multiselect('Select columns', df['leeftijd'].unique())
st.write(df.loc[df['leeftijd'].isin(options)])
