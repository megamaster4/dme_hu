from pathlib import Path
import sys

import altair as alt
import numpy as np
import polars as pl
import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.shared_code import get_data_gemeentes, get_data_gemeentes_bodemgebruik, growth_columns_by_year


def main():
    st.set_page_config(
        page_title="Bevolkingsgroei vs Bodemgebruik",
    )
    df_bevolking = get_data_gemeentes()
    df_bodem = get_data_gemeentes_bodemgebruik()
    devdf_bevolking = df_bevolking.clone()
    devdf_bodem = df_bodem.clone()

    st.markdown(
        """
        ## Bevolkingsgroei vs Bodemgebruik
        Om te bepalen welke variabelen de grootste invloed hebben op de bevolkingsgroei, is er gekeken naar de correlatie tussen de bevolkingsgroei en de verschillende bodemgebruik categorieën.
        
        ### Correlatie tussen bevolkingsgroei en bodemgebruik
        De correlatie is gemaakt door gebruik te maken van alle features van alle gemeentes, over de periodes waarbij ook het bodemgebruik is gerapporteerd.
        
        De onderstaande staafdiagram geeft de correlatie weer tussen de bevolkingsgroei en de verschillende bodemgebruik categorieën, onderverdeeld in hoofdcategorieën en subcategorieën.
        """
    )

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

    # Use a clone of the data for model training
    model_df = devdf_bodem.clone().to_pandas()

    use_cols = [col for col in devdf_bodem.columns if col not in exclude_cols]

    # Calculate the correlation matrix
    correlation_matrix = (
        devdf_bodem.select(use_cols)
        .corr()
        .with_columns(index=pl.lit(use_cols))
        .melt(id_vars=["index"])
        .filter((pl.col("index") != pl.col("variable")))
    )
    correlation_matrix = correlation_matrix.filter(
        pl.col("variable") == "bevolking_1_januari_growth"
    )

    # Remove totale oppervlakte from the correlation matrix
    correlation_matrix = correlation_matrix.filter(
        ~pl.col("index").str.starts_with("totale_")
    )

    hoofd_categories, sub_categories = st.tabs(["Hoofdcategorieën", "Subcategorieën"])

    with hoofd_categories:
        # filter correlation_matrix on hoofdcategorieën
        correlation_matrix_hoofd = correlation_matrix.filter(
            pl.col("index").str.starts_with("totaal_")
        )

        # Create a heatmap for the correlation matrix using Altair
        heatmap = (
            alt.Chart(correlation_matrix_hoofd)
            .mark_bar()
            .encode(
                x=alt.X("value", axis=alt.Axis(title="Correlatie"), stack="zero"),
                y=alt.Y("index:O", sort="-x"),
            )
            .properties(
                title="Correlatie tussen bevolkingsgroei en bodemgebruik",
                height=500,
            )
        )
        st.altair_chart(heatmap, use_container_width=True)

    with sub_categories:
        # filter correlation_matrix on hoofdcategorieën
        correlation_matrix_sub = correlation_matrix.filter(
            ~pl.col("index").str.starts_with("totaal_")
        )

        # Create a heatmap for the correlation matrix using Altair
        heatmap = (
            alt.Chart(correlation_matrix_sub)
            .mark_bar()
            .encode(
                x=alt.X("value", axis=alt.Axis(title="Correlatie"), stack="zero"),
                y=alt.Y("index:O", sort="-x"),
            )
            .properties(
                title="Correlatie tussen bevolkingsgroei en bodemgebruik",
                height=500,
            )
        )
        st.altair_chart(heatmap, use_container_width=True)

    st.markdown(
        """
        Zoals verwacht heeft een groei in woonterrein erg hoge postieve correlatie met de bevolkingsgroei. Maar ook een groei in sportterrein en wegverkeersterrein hebben beide een correlatie van boven de 0.8.

        ## Voorspellen bevolkingsgroei
        Om de bevolkingsgroei te voorspellen, wordt er gebruik gemaakt van verschillende soort modellen. De features die gebruikt worden zijn de bodemgebruik categorieën met een correlatie van boven de 0.5.
        """
    )
    correlation_matrix_sub = correlation_matrix_sub.filter(pl.col("value") > 0.5)
    st.dataframe(correlation_matrix_sub.to_pandas(), use_container_width=True)

    st.markdown(
        """
        Deze features met correlaties hoger dan 0.5 kunnen gebruikt worden om de bevolkingsgroei te voorspellen. De volgende lijngrafiek laat de samenhang goed zien, al zien we wel dat de variabele `bedrijventerrein_growth` in het begin minder samenhangt dan de overige features.
        """
    )

    use_cols_corr = correlation_matrix_sub["index"].to_list()
    use_cols_corr.extend(["bevolking_1_januari_growth", "jaar"])

    model_df = model_df.loc[:, use_cols_corr]
    model_df = model_df.set_index("jaar")

    model_df_avg = model_df.groupby("jaar").mean()

    model_df_melted = model_df_avg.reset_index().melt(id_vars=["jaar"])

    # Plot the average growth per year with altair
    line_chart = (
        alt.Chart(model_df_melted)
        .mark_line()
        .encode(
            x="jaar:O",
            y="value:Q",
            color="variable:N",
        )
        .properties(
            title="Gemiddelde bevolkingsgroei per jaar vs Bodemgebruik met correlatie > 0.5",
            height=500,
        )
    )

    st.altair_chart(line_chart, use_container_width=True)


if __name__ == "__main__":
    main()
