import pytest
import stellar
import tempfile


class TestCase(object):
    @pytest.yield_fixture(autouse=True)
    def config(self, monkeypatch):
        with tempfile.NamedTemporaryFile() as tmp:
            def load_test_config(self):
                self.config = {
                    'stellar_url': 'sqlite:///%s' % tmp.name,
                    'url': 'sqlite:///%s' % tmp.name,
                    'project_name': 'test_project',
                    'tracked_databases': ['test_database'],
                    'TEST': True
                }
                return None
            monkeypatch.setattr(stellar.app.Stellar, 'load_config', load_test_config)
            yield


class Test(TestCase):
    def test_setup_method_works(self, monkeypatch):
        monkeypatch.setattr(
            stellar.app.Stellar,
            'create_stellar_database',
            lambda x: None
        )
        app = stellar.app.Stellar()
        for key in (
            'TEST',
            'stellar_url',
            'url',
            'project_name',
            'tracked_databases',
        ):
            assert app.config[key]

    def test_shows_not_enough_arguments(self):
        with pytest.raises(SystemExit) as e:
            stellar.command.main()

    def test_app_context(self, monkeypatch):
        monkeypatch.setattr(
            stellar.app.Stellar,
            'create_stellar_database',
            lambda x: None
        )
        app = stellar.app.Stellar()
