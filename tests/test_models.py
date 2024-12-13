from stellar.models import get_unique_hash, Table, Snapshot


def test_get_unique_hash():
    assert get_unique_hash()
    assert get_unique_hash() != get_unique_hash()
    assert len(get_unique_hash()) == 32


def test_table():
    table = Table(
        table_name='hapsu',
        snapshot=Snapshot(
            snapshot_name='snapshot',
            project_name='myproject',
            hash='3330484d0a70eecab84554b5576b4553'
        )
    )
    assert len(table.get_table_name('master')) == 24
