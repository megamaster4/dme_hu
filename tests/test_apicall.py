import pytest
import requests
from backend.utils import parse_response_metadata
from backend import models


def test_get_burgstaat(mocker):
    response = requests.Response()
    response.status_code = 200
    with open("tests/test_data/burgstaat.xml", "rb") as f:
        response._content = f.read()
    
    mocker.patch("requests.get", return_value=response)
    result = parse_response_metadata("https://opendata.cbs.nl/ODataFeed/odata/03759ned/BurgerlijkeStaat", object=models.Burgstaat)
    
    assert result[1].burgerlijkestaat == "Ongehuwd"
    assert result[2].burgst_key == '1020   '
    assert result[2].burgerlijkestaat == "Gehuwd"
