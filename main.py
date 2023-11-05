from pathlib import Path

import click
from loguru import logger
from tqdm import tqdm
from sklearn import linear_model, svm, tree, kernel_ridge

from backend.config import Settings
from backend import crud, utils
from backend.db_tools import DBEngine
from backend.models import (
    Bevolking,
    Bodemgebruik,
    Regios,
    Burgstaat,
    CategoryGroup,
    Geslacht,
    Leeftijd,
    Perioden,
)
from backend.utils import (
    get_data_from_cbs,
    get_metadata_from_cbs,
    parse_parquet_to_db,
    train_models,
)


@click.command()
@click.option(
    "--callapi", is_flag=True, help="Call CBS Statline API to get metadata and data."
)
@click.option(
    "--num-processes",
    default=4,
    help="Number of processes to use for downloading data from CBS Statline API.",
)
@click.option(
    "--process-parquet",
    default="",
    help="Path to folder with parquet files to process and upsert into database.",
)
@click.option(
    "--setup-models", is_flag=True, help="Train models and save to ml_models folder."
)
def main(callapi: bool, num_processes: int, process_parquet: str, setup_models: bool):
    # Connect to database and create engine
    db_engine = DBEngine(**Settings().model_dump())

    if callapi:
        # Get metadata from CBS Statline API and upsert into database
        models_dict = {
            "BurgerlijkeStaat": Burgstaat,
            "CategoryGroups": CategoryGroup,
            "Geslacht": Geslacht,
            "Leeftijd": Leeftijd,
            "Perioden": Perioden,
            "RegioS": Regios,
        }

        get_metadata_from_cbs(db_engine=db_engine, models_dict=models_dict)
        # Get data from CBS Statline API and save as parquet files
        get_data_from_cbs(
            object=Bodemgebruik,
            url="https://opendata.cbs.nl/ODataFeed/odata/70262ned/TypedDataSet",
            num_processes=num_processes,
        )
        get_data_from_cbs(
            object=Bevolking,
            url="https://opendata.cbs.nl/ODataFeed/odata/03759ned/TypedDataSet",
            num_processes=num_processes,
        )

    if process_parquet != "":
        # Get regio keys from database
        regios = crud.select_table_from_db(db_engine=db_engine, table=Regios)
        regio_keys = regios["regio_key"].unique()

        # Parse parquet files and upsert into database
        folders = {
            Bodemgebruik: Path(f"{process_parquet}/bodemgebruik"),
            Bevolking: Path(f"{process_parquet}/bevolking"),
        }
        for object, folder in folders.items():
            parquetFiles = folder.rglob("*.parquet")
            nrows = len(list(parquetFiles))
            logger.info(f"Found {nrows} parquet files in {folder}.")
            for file in tqdm(folder.iterdir(), total=nrows):
                if file.suffix == ".parquet":
                    parse_parquet_to_db(
                        path=file, object=object, db_engine=db_engine, regios=regio_keys
                    )

    if setup_models:
        # Train models and save them to the ml_models folder
        df_bevolking = crud.get_data_gemeentes(_db_engine=db_engine)
        df_bodem = crud.get_data_gemeentes_bodemgebruik(_db_engine=db_engine)

        # Preprocessing of data, such as only using regio's that are in both datasets, and filling null values
        regios = df_bevolking["regio"].to_list()
        exclude_cols = ["regio", "jaar", "geslacht", "catgroup", "burgerlijkestaat"]
        devdf_bodem = df_bodem.filter(df_bodem["regio"].is_in(regios))
        devdf_bodem = devdf_bodem.fill_null(strategy="zero")
        devdf_bodem = utils.growth_columns_by_year(
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
            "bevolking_1_januari_growth",
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
        models = {
            "LinearRegression": linear_model.LinearRegression(),
            "SVM": svm.SVR(),
            "DecisionTreeRegressor": tree.DecisionTreeRegressor(),
            "KernelRidgeRegression": kernel_ridge.KernelRidge(),
        }

        # Train the models and save them to the ml_models folder
        train_models(X=X, y=y, models=models)


if __name__ == "__main__":
    main()
