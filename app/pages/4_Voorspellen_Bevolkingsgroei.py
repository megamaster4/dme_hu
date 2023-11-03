from pathlib import Path
import sys

import numpy as np
import polars as pl
import pandas as pd
import streamlit as st
from sklearn import linear_model, svm, tree, kernel_ridge
from sklearn.model_selection import train_test_split
from sqlalchemy import select

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.shared_code import get_data_gemeentes, get_data_gemeentes_bodemgebruik, growth_columns_by_year

@st.cache_resource()
def train_models(X_train, y_train, X_test, y_test):
    models = {
        "LinearRegression": linear_model.LinearRegression(),
        "SVM": svm.SVR(),
        "DecisionTreeRegressor": tree.DecisionTreeRegressor(),
        "KernelRidgeRegression": kernel_ridge.KernelRidge(),
    }
    trained_models = {}
    outcomes = {}

    # Fit all 4 models and print the scores in a tab
    for modelName, model in models.items():
        model.fit(X_train, y_train)
        trained_models[modelName] = model
        outcomes[modelName] = model.score(X_test, y_test)

    return trained_models, outcomes

def main():
    st.markdown(
        """
        ## Voorspellen van Bevolkingsgroei
        Om de bevolkingsgroei te voorspellen, wordt er gebruik gemaakt van verschillende soort modellen. De features die gebruikt worden zijn de reeds genoemde categorieën met een correlatie van boven de 0.5.
        De volgende modellen worden gebruikt:
        - Linear Regression
        - Support Vector Machine
        - Decision Tree Regressor
        - Kernel Ridge Regression

        In eerste instantie wordt de data opgesplitst in een test- en trainingsdataset met een verhouding van 80% trainingsdata en 20% testdata. Vervolgens worden de modellen getraind op de trainingsdata en wordt de score van het model berekend op de testdata. De score geeft aan hoe goed het model de testdata kan voorspellen. De score is een waarde tussen de 0 en 1, waarbij 1 betekent dat het model de testdata perfect kan voorspellen.
        De onderstaande tabs geven respectievelijk per model de score. Vervolgens wordt in een tabel de actual en predicted waardes naast elkaar gezet, zodat de voorspellingen van de modellen vergeleken kunnen worden met de werkelijke waardes.
        """
    )

    df_bevolking = get_data_gemeentes()
    df_bodem = get_data_gemeentes_bodemgebruik()
    devdf_bevolking = df_bevolking.clone()
    devdf_bodem = df_bodem.clone()

    regios = devdf_bevolking["regio"].to_list()
    exclude_cols = ["regio", "jaar", "geslacht", "catgroup", "burgerlijkestaat"]
    devdf_bodem = df_bodem.filter(df_bodem["regio"].is_in(regios))
    devdf_bodem = devdf_bodem.fill_null(strategy="zero")
    devdf_bodem = growth_columns_by_year(
        df=devdf_bodem, columns_to_exclude=exclude_cols
    )
    devdf_bodem = devdf_bodem[
        [s.name for s in devdf_bodem if not (s.null_count() == devdf_bodem.height)]
    ]
    devdf_bodem = devdf_bodem.drop_nulls("bevolking_1_januari_growth")

    devdf_bodem = devdf_bodem.select(
        [
            col
            for col in devdf_bodem.columns
            if (col in exclude_cols) or (col.endswith("growth"))
        ]
    )

    # Use a clone of the data for model training, and pick the features with the highest correlations
    include_cols = [
        "wegverkeersterrein_growth",
        "woonterrein_growth",
        "bedrijventerrein_growth",
        "begraafplaats_growth",
        "sportterrein_growth",
        "volkstuin_growth",
        "overig_agrarisch_terrein_growth",
        "jaar",
        "bevolking_1_januari_growth"
        ]
    model_df = devdf_bodem.clone().select(include_cols).to_pandas()
    model_df.set_index("jaar", inplace=True)

    # Split the data into train and test sets
    X = model_df[
        [
            col
            for col in model_df.columns
            if col not in ["bevolking_1_januari_growth", "jaar"]
        ]
    ]
    
    y = model_df["bevolking_1_januari_growth"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    linearModel, svmModel, decisiontreeModel, kernelridgeModel = st.tabs(
        [
            "Linear Regression",
            "Support Vector Machine",
            "Decision Tree Regressor",
            "Kernel Ridge Regression",
        ]
    )
    
    trained_models, outcomes = train_models(X_train, y_train, X_test, y_test)

    with linearModel:
        st.markdown(
            f"""
        ### Linear Regression
        De score van het lineare model is: {outcomes["LinearRegression"]}
        """
        )

    with svmModel:
        st.markdown(
            f"""
        ### Support Vector Machine
        De score van het SVM model is: {outcomes["SVM"]}
        """
        )

    with decisiontreeModel:
        st.markdown(
            f"""
        ### Decision Tree Regressor
        De score van het Decision Tree Regressor model is: {outcomes["DecisionTreeRegressor"]}
        """
        )

    with kernelridgeModel:
        st.markdown(
            f"""
        ### Kernel Ridge Regression
        De score van het Kernel Ridge Regression model is: {outcomes["KernelRidgeRegression"]}
        """
        )

    max_outcome_key = max(outcomes, key=outcomes.get)

    st.markdown(
        f"""
        ## Voorspellingen
        The model met de hoogste score is {max_outcome_key}. De voorspellingen voor alle modellen zijn hieronder te zien.
        """
    )

    # Create pandas dataframe to compare the predicted and actual values, with the actual and predicted columns next to each other
    df = pd.DataFrame()
    df["year"] = X_test.index
    df["actual"] = y_test.to_list()

    for modelName, model in trained_models.items():
        df[modelName] = model.predict(X_test)

    st.dataframe(df, use_container_width=True)


    with st.form("voorspellingen"):
        st.markdown(
            """
            ## DIY Voorspellingen
            Na het trainen van de modellen is het mogelijk om zelf een voorspelling te doen. Dit kan gedaan worden door de sliders te gebruiken om de groei in bodemgebruik in te stellen. De sliders zijn zo ingesteld dat de groei tussen de -1 en 1 kan liggen. Een waarde van 0 betekent dat er geen groei is, een waarde van 1 betekent dat er een groei is van 100%.
            Als de waardes voor de features zijn gekozen, kan er op de knop `Voorspel` worden gedrukt. De voorspelling in bevolkingsgroei wordt dan weergegeven.
            """
        )

        woonterrein_slider = st.slider(
            "Groei in Woonterrein", min_value=-1.0, max_value=1.0, value=0.0, step=0.01
        )
        bedrijventerrein_slider = st.slider(
            "Groei in Bedrijventerrein", min_value=-1.0, max_value=1.0, value=0.0, step=0.01
        )
        begraafplaats_slider = st.slider(
            "Groei in Begraafplaats",min_value=-1.0, max_value=1.0, value=0.0, step=0.01
        )
        sportterrein_slider = st.slider(
            "Groei in Sportterrein", min_value=-1.0, max_value=1.0, value=0.0, step=0.01
        )
        volkstuin_slider = st.slider(
            "Groei in Volkstuin", min_value=-1.0, max_value=1.0, value=0.0, step=0.01
        )
        overig_agrarisch_terrein_slider = st.slider(
            "Groei in Overig Agrarisch Terrein", min_value=-1.0, max_value=1.0, value=0.0, step=0.01
        )
        wegverkeersterrein_slider = st.slider(
            "Groei in Wegverkeersterrein", min_value=-1.0, max_value=1.0, value=0.0, step=0.01
        )
        best_model = st.selectbox("Selecteer een model", list(trained_models.keys()))
        voorspel = st.form_submit_button("Voorspel")

        if voorspel:
            voorspelling = trained_models[best_model].predict(
                np.array([
                    woonterrein_slider,
                    bedrijventerrein_slider,
                    begraafplaats_slider,
                    sportterrein_slider,
                    volkstuin_slider,
                    overig_agrarisch_terrein_slider,
                    wegverkeersterrein_slider,
                ]).reshape(1,-1)
            )
        
            st.toast('Voorspelling gelukt!', icon='✅')

            st.markdown(
                f"""
                ### De door jou ingevoerde gegevens over een groei in bodemgebruik zorgen voor een bevolkingsgroei van: 
                ## {voorspelling[0]*100:.2f}%
                """
            )



if __name__ == "__main__":
    main()
