import os
import sys

import altair as alt
import polars as pl
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn import linear_model
import numpy as np
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
        df = df.with_columns(
            ((pl.col(column) - pl.col(f'{column}_previous_moment'))/pl.col(f'{column}_previous_moment')).alias(f'{column}_growth')
        )
        df = df.fill_nan(0)

    # The following code is needed to replace inf values with 0, because of a bug in Polars.
    # We will replace them using pandas, and convert the dataframe back to polars before returning the dataframe
    df_pd = df.to_pandas()
    df_pd.replace([np.inf, -np.inf], 0, inplace=True)
    df = pl.from_pandas(df_pd)
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
        ## Bevolkingsgroei vs Bodemgebruik
        Om te bepalen welke variabelen de grootste invloed hebben op de bevolkingsgroei, is er gekeken naar de correlatie tussen de bevolkingsgroei en de verschillende bodemgebruik categorieën.
        
        ### Correlatie tussen bevolkingsgroei en bodemgebruik
        De correlatie is gemaakt door gebruik te maken van alle features van alle gemeentes, over de periodes waarbij ook het bodemgebruik is gerapporteerd.
        
        De onderstaande staafdiagram geeft de correlatie weer tussen de bevolkingsgroei en de verschillende bodemgebruik categorieën, onderverdeeld in hoofdcategorieën en subcategorieën.
        """
    )

    regios = devdf_bevolking['regio'].to_list()
    exclude_cols=['regio', 'jaar', 'geslacht', 'catgroup', 'burgerlijkestaat']
    devdf_bodem = df_bodem.filter(df_bodem['regio'].is_in(regios))
    devdf_bodem = devdf_bodem.fill_null(strategy='zero')
    devdf_bodem = growth_columns_by_year(df=devdf_bodem, columns_to_exclude=exclude_cols)
    devdf_bodem = devdf_bodem[[s.name for s in devdf_bodem if not (s.null_count() == devdf_bodem.height)]]
    devdf_bodem = devdf_bodem.drop_nulls('bevolking_1_januari_growth')

    devdf_bodem = devdf_bodem.select([col for col in devdf_bodem.columns if (col in exclude_cols) or (col.endswith('growth'))])

    # Use a clone of the data for model training
    model_df = devdf_bodem.clone().to_pandas()

    use_cols = [col for col in devdf_bodem.columns if col not in exclude_cols]

    # Calculate the correlation matrix
    correlation_matrix = devdf_bodem.select(use_cols).corr().with_columns(index=pl.lit(use_cols)).melt(id_vars=['index']).filter((pl.col('index') != pl.col('variable')))
    correlation_matrix = correlation_matrix.filter(pl.col('variable') == 'bevolking_1_januari_growth')

    # Remove totale oppervlakte from the correlation matrix
    correlation_matrix = correlation_matrix.filter(~pl.col('index').str.starts_with('totale_'))

    hoofd_categories, sub_categories = st.tabs(['Hoofdcategorieën', 'Subcategorieën'])

    with hoofd_categories:
        # filter correlation_matrix on hoofdcategorieën
        correlation_matrix_hoofd = correlation_matrix.filter(pl.col('index').str.starts_with('totaal_'))

        # Create a heatmap for the correlation matrix using Altair
        heatmap = alt.Chart(correlation_matrix_hoofd).mark_bar().encode(
            x=alt.X('value', axis=alt.Axis(title='Correlatie'), stack='zero'),
            y=alt.Y('index:O', sort= '-x')
        ).properties(
            title='Correlatie tussen bevolkingsgroei en bodemgebruik',
            height=500,
        )
        st.altair_chart(heatmap, use_container_width=True)

    with sub_categories:
        # filter correlation_matrix on hoofdcategorieën
        correlation_matrix_sub = correlation_matrix.filter(~pl.col('index').str.starts_with('totaal_'))

        # Create a heatmap for the correlation matrix using Altair
        heatmap = alt.Chart(correlation_matrix_sub).mark_bar().encode(
            x=alt.X('value', axis=alt.Axis(title='Correlatie'), stack='zero'),
            y=alt.Y('index:O', sort= '-x')
        ).properties(
            title='Correlatie tussen bevolkingsgroei en bodemgebruik',
            height=500,
        )
        st.altair_chart(heatmap, use_container_width=True)
    
    st.markdown(
        """
        Zoals verwacht heeft een groei in woonterrein erg hoge postieve correlatie met de bevolkingsgroei. Maar ook een groei in sportterrein en wegverkeersterrein hebben beide een correlatie van boven de 0.8.

        ## Voorspellen bevolkingsgroei
        Om de bevolkingsgroei te voorspellen, wordt er gebruik gemaakt van verschillende soort modellen. De features die gebruikt worden zijn de bodemgebruik categorieën met een correlatie van boven de 0.5.
        """
    )
    correlation_matrix_sub = correlation_matrix_sub.filter(pl.col('value') > 0.5)
    st.dataframe(correlation_matrix_sub.to_pandas(), use_container_width=True)
    
    use_cols_corr = correlation_matrix_sub['index'].to_list()
    use_cols_corr.extend(['bevolking_1_januari_growth', 'jaar'])
    print(use_cols_corr)
    # use_cols_corr.extend(exclude_cols)
    model_df = model_df.loc[:, use_cols_corr]
    model_df = model_df.set_index('jaar')

    # Split the data into train and test sets
    X = model_df[[col for col in model_df.columns if col not in ['bevolking_1_januari_growth', 'jaar']]]
    y = model_df['bevolking_1_januari_growth']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    linearModel, svmModel = st.tabs(['Linear Regression', 'Support Vector Machine'])

    with linearModel:
        reg = linear_model.LinearRegression()
        reg.fit(X_train, y_train)

        # Predict the test set
        y_pred = reg.predict(X_test)
        r2_score = reg.score(X_test, y_test)

        st.markdown(
        f"""
        ### Linear Regression
        De score van het lineare model is: {r2_score}
        
        """
        )

    with svmModel:
        reg = svm.SVR()
        reg.fit(X_train, y_train)

        # Predict the test set
        y_pred = reg.predict(X_test)
        r2_score = reg.score(X_test, y_test)

        st.markdown(
        f"""
        ### Support Vector Machine
        De score van het SVM model is: {r2_score}
        
        """
        )

    # # create a Pandas DataFrame with the predicted and actual values
    # df_actual = pd.DataFrame({'value': y_test, 'year': y_test.index, 'type': 'actual'})
    # df_pred = pd.DataFrame({'value': y_pred, 'year': y_test.index, 'type': 'predicted'})
    # df = pd.concat([df_actual, df_pred], ignore_index=True)

    # # create a scatter plot of the predicted and actual values
    # scatter_plot = alt.Chart(df).mark_point().encode(
    #     x=alt.X('year', scale=alt.Scale(domain=[1996, 2020])),
    #     y='value',
    #     color='type'
    # )

    # st.altair_chart(scatter_plot, use_container_width=True)
    

if __name__ == "__main__":
    main()