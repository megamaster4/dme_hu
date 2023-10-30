from backend.db_tools import DBEngine
from backend.config import Settings, DFType
from backend import crud, models, utils
import requests


def test_get_connection():
    db_engine = DBEngine(**Settings().model_dump())
    assert db_engine.engine.connect() is not None


def test_insert_data(mocker):
    db_engine = DBEngine(**Settings().model_dump())
    models_dict = {
        "BurgerlijkeStaat": models.Burgstaat,
    }
    response = requests.Response()
    response.status_code = 200
    with open("tests/test_data/burgstaat.xml", "rb") as f:
        response._content = f.read()

    mocker.patch("requests.get", return_value=response)
    utils.get_metadata_from_cbs(db_engine=db_engine, models_dict=models_dict)

    df = crud.fetch_data(
        stmt=models.Burgstaat.__table__.select(),
        db_engine=db_engine,
        package=DFType.POLARS,
    )

    assert df.shape[0] == 5
    assert df.select("burgerlijkestaat")[1].to_numpy() == "Ongehuwd"
    assert df.select("burgst_key")[3].to_numpy() == "1050   "
