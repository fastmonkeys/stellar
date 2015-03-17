import tempfile
import subprocess

import os
import pytest

from . import get_conn
from stellar.app import Stellar


class StellarTest(Stellar):
    def load_config(self):
        self.config = {
            'stellar_url': 'postgresql://localhost:5432/stellar_data',
            'url': 'postgresql://localhost:5432/template1',
            'project_name': 'sample',
            'tracked_databases': ['tmp_sample']
        }


def execute(cmd, cwd):
    return subprocess.Popen(
        'python -m stellar %s' % cmd, shell=True, cwd=cwd
    ).wait()

@pytest.fixture
def stellar():
    return StellarTest()


def test_snapshotting_and_restoring(pg_database, stellar):
    stellar.operations.create_database('tmp_sample')
    conn = get_conn('postgresql://localhost:5432/tmp_sample')
    conn.execute('''
        CREATE TABLE players (name VARCHAR(20))
    ''')
    conn.execute('''
        INSERT INTO players VALUES ('Hello world')
    ''')


    cwd = tempfile.mkdtemp()
    with open(os.path.join(cwd, 'stellar.yaml'), 'w') as fp:
        fp.write("""
project_name: sample
stellar_url: postgresql://localhost:5432/stellar_data
tracked_databases: [tmp_sample]
url: postgresql://localhost:5432/template1
        """)
    assert not execute('snapshot', cwd=cwd)

    conn = get_conn('postgresql://localhost:5432/tmp_sample')
    conn.execute('''
        UPDATE players SET name = 'ruined'
    ''')


    assert not execute('restore', cwd=cwd)

    conn = get_conn('postgresql://localhost:5432/tmp_sample')
    assert conn.execute(
        'SELECT name FROM players'
    ).fetchone()[0] == 'Hello world'
