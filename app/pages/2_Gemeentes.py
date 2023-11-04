from pathlib import Path
import sys

import altair as alt
import polars as pl
import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.shared_code import (
    get_data_gemeentes,
    get_data_gemeentes_bodemgebruik,
    divide_columns_by_column,
    extract_top5,
)


def main():
    st.set_page_config(
        page_title="Bevolkingsgroei Gemeentes",
    )
    df_bevolking = get_data_gemeentes()
    df_bodem = get_data_gemeentes_bodemgebruik()
    aantal_gemeentes = df_bodem.clone()
    devdf = df_bevolking.clone()

    st.markdown(
        """
        ## Bevolkingsgroei per Gemeente
        In dit tabblad wordt er gekeken naar de bevolkingsgroei van actieve gemeentes in Nederland. Omdat het voor kan komen dat een gemeente is opgeheven, wordt
        alleen gekeken naar gemeentes die in het jaar 2023 nog actief zijn. Het onderstaande overzicht geeft weer welke gemeentes dat zijn:
        """
    )
    aantal_gemeentes = aantal_gemeentes.filter(pl.col("jaar") == pl.col("jaar").max())
    aantal_gemeentes = aantal_gemeentes.filter(
        pl.col("bevolking_1_januari").is_not_null()
    )
    st.dataframe(
        aantal_gemeentes.select(
            pl.col("regio"), pl.col("bevolking_1_januari")
        ).to_pandas(),
        use_container_width=True,
    )

    st.markdown(
        """

        De top 5 gemeentes met de hoogste relatieve en absolute groei, in de afgelopen 5 jaar, worden hieronder weergegeven.
        """
    )

    devdf = extract_top5(df=devdf, only_active=True)
    devdf_max_year = devdf.filter(pl.col("jaar") == pl.col("jaar").max())
    relatief, absolute = st.tabs(["Top 5 Relatieve Groei", "Top 5 Absolute Groei"])

    with relatief:
        st.markdown(
            """
            ### Top 5 Relatieve Groei
            De top 5 gemeentes met de hoogste relatieve groei in de afgelopen 5 jaar:
            """
        )

        df_relatief = devdf_max_year.sort("percentage_growth", descending=True).head(5)
        chart = (
            alt.Chart(df_relatief)
            .mark_bar()
            .encode(
                x=alt.X("percentage_growth:Q", axis=alt.Axis(format="%"), stack="zero"),
                y=alt.Y("regio", sort="-x"),
            )
            .properties(height=600, width=800)
        )
        st.altair_chart(chart, use_container_width=True)

    with absolute:
        st.markdown(
            """
            ### Top 5 Absolute Groei
            De top 5 gemeentes met de hoogste absolute groei in de afgelopen 5 jaar:
            """
        )
        df_absolute = devdf_max_year.sort("absolute_growth", descending=True).head(5)
        chart = (
            alt.Chart(df_absolute)
            .mark_bar()
            .encode(x="absolute_growth", y=alt.Y("regio", sort="-x"))
            .properties(height=600, width=800)
        )
        st.altair_chart(chart, use_container_width=True)

    st.markdown(
        """
        Hoe komt het dat de gemeente Amsterdam zo'n grote groei heeft? En waarom is de gemeente Noordwijk zo'n uitschieter qua relatieve groei?

        We gaan het bodemgebruik toevoegen aan zowel de gemeente Amsterdam als Noordwijk om te kijken of we hier een verklaring voor kunnen vinden.

        ## Bodemgebruik Amsterdam en Noordwijk
        Om een goede vergelijking te kunnen geven, wordt er gekeken naar het relatieve bodemgebruik ten opzichte van het totale oppervlakte van de gemeente.
        """
    )

    devdf_bodem = df_bodem.clone()
    # devdf_bodem = devdf_bodem.filter(pl.col("regio").is_in(["Amsterdam", "Noordwijk"]))

    exclude_cols = [
        "regio",
        "jaar",
        "bevolking_1_januari",
        "geslacht",
        "catgroup",
        "burgerlijkestaat",
    ]
    df_divided = divide_columns_by_column(
        devdf_bodem,
        divide_by_column="totale_oppervlakte",
        columns_to_exclude=exclude_cols,
    )

    df_divided = df_divided[
        [s.name for s in df_divided if not (s.null_count() == df_divided.height)]
    ]
    df_divided = df_divided.filter(pl.col("jaar") == pl.col("jaar").max())

    df_distribution = df_divided.melt(
        id_vars="regio",
        value_name="relative_percentage",
        value_vars=[
            col
            for col in df_divided.columns
            if (col.startswith("totaal")) and (col.endswith("relative"))
        ],
    )

    df_distribution = df_distribution.drop_nulls("relative_percentage")

    chart_stacked = (
        alt.Chart(
            df_distribution.filter(pl.col("regio").is_in(["Amsterdam", "Noordwijk"]))
        )
        .mark_bar()
        .encode(
            x=alt.X("regio:N", axis=alt.Axis(title="Groups")),
            y=alt.Y(
                "sum(relative_percentage):Q",
                axis=alt.Axis(format="%"),
                stack="normalize",
            ),
            color=alt.Color("variable:N", title="Categories"),
            order=alt.Order("relative_percentage:N", sort="ascending"),
        )
        .properties(title="Verdeling bodemgebruik per Gemeente", height=600, width=800)
    )
    st.altair_chart(chart_stacked, use_container_width=True)

    st.markdown(
        """
        Zo zien we dat de gemeente Amsterdam (absolute groei van 64070 inwoners) een groot deel van het oppervlakte gebruikt voor bebouwing, terwijl de gemeente Noordwijk (relatieve groei van 73,39%) een groot deel van het oppervlakte gebruikt voor bebossing of open natuurgebieden.
        
        ### Willekeurige Gemeente
        Voor verdere verdieping in geen gemeente naar keuze, gebruik onderstaande dropdown om een gemeente te selecteren. Merk op dat hier niet alle gemeentes in staan, maar alleen de gemeentes die in 2023 nog actief zijn & een geregistreerd bodemgebruik hebben.
        """
    )

    regios = df_distribution.unique(subset=["regio"]).sort("regio").select("regio")
    option = st.selectbox(
        label="Selecteer een Gemeente", options=regios.to_pandas()["regio"].tolist()
    )

    toggle_subcats = st.toggle("Sub-categorieën", value=False)

    if toggle_subcats:
        df_distribution = df_divided.melt(
            id_vars="regio",
            value_name="relative_percentage",
            value_vars=[
                col
                for col in df_divided.columns
                if not (col.startswith("totaal_")) and (col.endswith("relative"))
            ],
        )

    else:
        df_distribution = df_divided.melt(
            id_vars="regio",
            value_name="relative_percentage",
            value_vars=[
                col
                for col in df_divided.columns
                if (col.startswith("totaal_")) and (col.endswith("relative"))
            ],
        )

    chart_stacked_custom = (
        alt.Chart(df_distribution.filter(pl.col("regio").is_in([option])))
        .mark_bar()
        .encode(
            x=alt.X("regio:N", axis=alt.Axis(title="Groups")),
            y=alt.Y(
                "sum(relative_percentage):Q",
                axis=alt.Axis(format="%"),
                stack="normalize",
            ),
            color=alt.Color("variable:N", title="Categories"),
            order=alt.Order("relative_percentage:N", sort="ascending"),
        )
        .properties(title="Verdeling bodemgebruik per Gemeente", height=600, width=800)
    )
    st.altair_chart(chart_stacked_custom, use_container_width=True)


if __name__ == "__main__":
    main()
