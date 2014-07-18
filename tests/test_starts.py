import pytest
import stellar

class BaseTest(object):
    def setup_method(self, method):
        self._config = stellar.config.config
        stellar.config.config = {
            'lol': 'lol'
        }

    def teardown_method(self, method):
        stellar.config.config = self._config
        # monkeypatch.setattr(stellar.config, 'config', {
        #     'lol': 'lol'
        # })


class Test(BaseTest):
    def test_setup_method_works(self):
        assert stellar.config.config == {'lol': 'lol'}

    def test_shows_not_enough_arguments(self):
        with pytest.raises(SystemExit) as e:
            stellar.command.main()
