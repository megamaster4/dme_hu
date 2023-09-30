from pydantic import Field
from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    db_name: str = Field(alias='DBNAME')
    db_user: str = Field(alias='DBUSER')
    db_pass: str = Field(alias='DBPASS')
    db_port: str = Field(alias='DBPORT')


class DFType(Enum):
    """Enum for dataframe types."""
    POLARS = 1
    PANDAS = 2
