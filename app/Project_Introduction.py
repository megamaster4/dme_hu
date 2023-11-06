import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

st.set_page_config(
    page_title="Project Introduction",
)

st.title(
    "Hoe kunnen diverse soorten groei in bodemgebruik de relatieve bevolkingsgroei in gemeentes bepalen?"
)

st.markdown(
    """
    ## Project Introductie
    Dit onderzoek zal zich dus vooral richten op het analyseren van de correlaties tussen bevolkingsgroei en verschillende vormen van bodemgebruik. 
    Het verkrijgen van inzicht in de invloed van bevolkingsgroei op bodemgebruik zal verschillende belanghebbenden ten goede komen, waaronder lokale overheden, stedelijke planners, milieubeschermingsinstanties en ontwikkelaars. 
    De resultaten zullen helpen bij het informeren en vormgeven van strategieën met betrekking tot toekomstige ruimtelijke ordening, landgebruik en infrastructuurontwikkelingen in de gemeente.

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
    In de verschillende tabbladen wordt stilgestaand bij verschillende vraagstukken omtrent de bevolkingsgroei en bodemgebruik van de gemeentes in Nederland.
    """
)

st.sidebar.success("Selecteer een tabblad om te beginnen")
