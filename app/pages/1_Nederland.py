from pathlib import Path
import sys

import polars as pl
import altair as alt
import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.shared_code import (
    get_bevolking_landelijk,
    get_bodemgebruik_landelijk,
    divide_columns_by_column,
)


def main():
    st.set_page_config(
        page_title="Nederland",
    )

    st.markdown(
        """
        ## Nederland
        In dit tabblad wordt er gekeken naar statistieken omtrent bevolkingsgroei en bodemgebruik in Nederland, van het jaar 1988 tot en met 2023.
        """
    )

    df = get_bevolking_landelijk()

    st.markdown(
        """
        ### Jaarlijkse totale groei Nederland
        De jaarlijkse totale groei van de bevolking in Nederland, van het jaar 1988 tot en met 2023, is als volgt:
        """
    )
    toggle_geslacht = st.toggle("Split op geslacht", value=False)

    if toggle_geslacht:
        df_geslacht = df.filter(pl.col("geslacht") != "Totaal mannen en vrouwen")
        st.bar_chart(
            data=df_geslacht.to_pandas(),
            x="jaar",
            y="bevolking_1_januari",
            color="geslacht",
            height=600,
            width=800,
        )
    else:
        df_geslacht = df.filter(pl.col("geslacht") == "Totaal mannen en vrouwen")
        st.bar_chart(
            data=df_geslacht.to_pandas(),
            x="jaar",
            y="bevolking_1_januari",
            height=600,
            width=800,
        )

    st.markdown(
        """
        ### Relatieve groei Nederland
        De relatieve groei van Nederland, van het jaar 1988 tot en met 2023, is als volgt:
        """
    )
    radio_rel_abs = st.radio(
        "Relatieve of absolute groei?",
        ("Relatief", "Absoluut"),
        label_visibility="hidden",
    )

    df_growth = df.filter(pl.col("geslacht") == "Totaal mannen en vrouwen")
    df_growth = df_growth.with_columns(
        (pl.col("bevolking_1_januari").shift(1)).over("regio").alias("previous_year")
    )
    df_growth = df_growth.with_columns(
        (
            (pl.col("bevolking_1_januari") - pl.col("previous_year"))
            / pl.col("previous_year")
            * 100
        ).alias("relative_growth")
    )
    df_growth = df_growth.with_columns(
        (pl.col("bevolking_1_januari") - pl.col("previous_year")).alias(
            "absolute_growth"
        )
    )

    if radio_rel_abs == "Relatief":
        st.line_chart(
            data=df_growth.to_pandas(),
            x="jaar",
            y="relative_growth",
            height=600,
            width=800,
        )
    elif radio_rel_abs == "Absoluut":
        st.line_chart(
            data=df_growth.to_pandas(),
            x="jaar",
            y="absolute_growth",
            height=600,
            width=800,
        )

    st.markdown(
        """
        ## Bodemgebruik in Nederland
        Het bodemgebruik in Nederland is als volgt:
        """
    )
    df_bodemgebruik = get_bodemgebruik_landelijk()
    df_bodemgebruik = df_bodemgebruik.filter(pl.col("jaar") == pl.col("jaar").max())

    exclude_cols = [
        "regio",
        "jaar",
        "bevolking_1_januari",
        "geslacht",
        "catgroup",
        "burgerlijkestaat",
    ]
    df_divided = divide_columns_by_column(
        df_bodemgebruik,
        divide_by_column="totale_oppervlakte",
        columns_to_exclude=exclude_cols,
    )
    df_divided = df_divided[
        [s.name for s in df_divided if not (s.null_count() == df_divided.height)]
    ]
    df_divided = df_divided.filter(pl.col("jaar") == pl.col("jaar").max())

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

    chart_stacked = (
        alt.Chart(df_distribution)
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


if __name__ == "__main__":
    main()
