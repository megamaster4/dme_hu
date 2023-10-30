import os
from pathlib import Path
from urllib.parse import urlparse

import psycopg2
import pytest
from testcontainers.postgres import PostgresContainer


class PGTestContainer(PostgresContainer):
    """
    Fix for localnpipe, which is not supported by sqlalchemy.
    See: https://github.com/testcontainers/testcontainers-python/issues/108
    """

    def get_connection_url(self):
        return super().get_connection_url().replace("localnpipe", "localhost")


@pytest.fixture(scope="session", autouse=True)
def postgresql_connection():
    # Will be executed before the first test
    pg_container = PGTestContainer(image="postgres:15.4")

    # Start the container
    pg_container.start()
    conn = urlparse(pg_container.get_connection_url())

    # Since connections in the functions all set by env variables
    os.environ["DBPORT"] = str(conn.port)
    os.environ["DBUSER"] = conn.username
    os.environ["DBPASS"] = conn.password
    os.environ["DBNAME"] = conn.path[1:]

    with psycopg2.connect(
        host=conn.hostname,
        port=os.environ["DBPORT"],
        user=os.environ["DBUSER"],
        password=os.environ["DBPASS"],
        database=os.environ["DBNAME"],
    ) as conn:
        yield conn

    # Will be executed after the last test
    pg_container.stop()


# Initialize tables used by all tests
@pytest.fixture(scope="session", autouse=True)
def init_db(postgresql_connection):
    init_db_path = str(Path(__file__).parent / "db_init.sql")
    with postgresql_connection.cursor() as cursor:
        cursor.execute(open(init_db_path, "r").read())

    postgresql_connection.commit()
