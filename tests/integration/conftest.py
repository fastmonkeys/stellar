import os

from . import get_conn
from stellar.operations import list_of_databases, remove_database
import pytest


def cleanup_database(conn):
    databases = list_of_databases(conn)
    for database in databases:
        if database.startswith('stellar') or database.startswith('tmp_'):
            remove_database(conn, database)


@pytest.yield_fixture
def pg_database():
    if not (
        os.environ.get('RUN_INTEGRATION_TESTS') or
        os.environ.get('TRAVIS')
    ):
        pytest.skip("Enviroment variable RUN_INTEGRATION_TESTS is false")
        return

    conn = get_conn('postgresql://localhost:5432/template1')
    cleanup_database(conn)
    yield
    #cleanup_database(conn)
