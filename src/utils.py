import requests
import xml.etree.ElementTree as ET
from loguru import logger

from typing import Union
from models import Burgstaat, CategoryGroup, Geslacht, Leeftijd, Perioden, Regios, Bevolking
from crud import upsert


def parse_response(url: str, object: Union[Burgstaat, CategoryGroup, Geslacht, Leeftijd, Perioden, Regios]) -> list[Union[Burgstaat, CategoryGroup, Geslacht, Leeftijd, Perioden, Regios]]:
    """Parse XML response from CBS Statline API."""
    row = {}
    lijst = []
    response = requests.get(url)
    response_xml = ET.fromstring(response.content)
    entries = response_xml.findall('.//{http://www.w3.org/2005/Atom}entry')
    for entry in entries:
        for key, value in object.__resp_keys__().items():
            param = find_in_schema(entry=entry, key=key)
            row[value] = param
        lijst.append(object(**row))
    return lijst


def parse_response_bevolking(object: Bevolking = Bevolking, direct_upsert: bool = True, **kwargs) -> Union[list[Bevolking], int]:
    """Parse Bevolking XML response from CBS Statline API."""
    skiprows = 22500000
    row = {}
    lijst = []
    while True:
        url = f'https://opendata.cbs.nl/ODataFeed/odata/03759ned/TypedDataSet?$skip={skiprows}'
        response = requests.get(url, stream=True)
        response_xml = ET.fromstring(response.content)
        entries = response_xml.findall('.//{http://www.w3.org/2005/Atom}entry')
        for entry in entries:
            for key, value in object.__resp_keys__().items():
                param = find_in_schema(entry=entry, key=key)
                row[value] = param
            lijst.append(object(**row))

        if len(entries) < 10000:
            skiprows += len(entries)
            break

        skiprows += 10000
        logger.info(f'Parsed {skiprows} rows.')

        if direct_upsert:
            upsert(db_engine=kwargs['db_engine'], table=Bevolking, data=lijst)
            lijst = []
    return (lijst, skiprows)


def find_in_schema(entry: ET.Element, key: str) -> Union[str, None]:
    """Find key in schema."""
    schema = '{http://schemas.microsoft.com/ado/2007/08/dataservices}'
    param = entry.find(f'.//{schema}{key}')
    if param is None:
        return None
    return param.text
