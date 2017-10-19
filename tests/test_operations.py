import pytest

from stellar.operations import _get_pid_column


class ConnectionMock(object):
    def __init__(self, version):
        self.version = version

    def execute(self, query):
        return self

    def first(self):
        return [self.version]


class TestGetPidColumn(object):
    @pytest.mark.parametrize('version', ['9.1', '8.9', '9.1.9', '8.9.9'])
    def test_returns_procpid_for_version_older_than_9_2(self, version):
        raw_conn = ConnectionMock(version=version)
        assert _get_pid_column(raw_conn) == 'procpid'

    @pytest.mark.parametrize(
        'version',
        ['9.2', '9.3', '10.0', '9.2.1', '10.1.1']
    )
    def test_returns_pid_for_version_equal_or_newer_than_9_2(self, version):
        raw_conn = ConnectionMock(version=version)
        assert _get_pid_column(raw_conn) == 'pid'
