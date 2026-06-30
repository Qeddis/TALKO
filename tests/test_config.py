import os
from unittest.mock import patch


class TestConfig:
    @patch.dict(os.environ, {"BOT_TOKEN": "test-token-123"}, clear=False)
    def test_bot_token_loaded(self):
        import importlib
        import config

        importlib.reload(config)
        assert config.BOT_TOKEN == "test-token-123"

    @patch.dict(os.environ, {"ADMIN_IDS": "111,222,333"}, clear=False)
    def test_admin_ids_parsed(self):
        import importlib
        import config

        importlib.reload(config)
        assert config.ADMIN_IDS == {111, 222, 333}

    @patch.dict(os.environ, {"ADMIN_IDS": ""}, clear=False)
    def test_admin_ids_empty(self):
        import importlib
        import config

        importlib.reload(config)
        assert config.ADMIN_IDS == set()

    @patch.dict(os.environ, {"ADMIN_IDS": "100, 200 , 300"}, clear=False)
    def test_admin_ids_with_spaces(self):
        import importlib
        import config

        importlib.reload(config)
        assert config.ADMIN_IDS == {100, 200, 300}

    @patch.dict(os.environ, {"ADMIN_IDS": "abc,def,123"}, clear=False)
    def test_admin_ids_ignores_non_numeric(self):
        import importlib
        import config

        importlib.reload(config)
        assert config.ADMIN_IDS == {123}

    @patch.dict(os.environ, {"REPORTS_FOR_BAN": "10"}, clear=False)
    def test_reports_for_ban(self):
        import importlib
        import config

        importlib.reload(config)
        assert config.REPORTS_FOR_BAN == 10

    @patch.dict(os.environ, {"SPAM_MAX_MESSAGES": "8"}, clear=False)
    def test_spam_max_messages(self):
        import importlib
        import config

        importlib.reload(config)
        assert config.SPAM_MAX_MESSAGES == 8

    @patch.dict(os.environ, {"SPAM_WINDOW_SECONDS": "5.5"}, clear=False)
    def test_spam_window_seconds(self):
        import importlib
        import config

        importlib.reload(config)
        assert config.SPAM_WINDOW_SECONDS == 5.5

    @patch.dict(
        os.environ,
        {
            "REPORTS_FOR_BAN": "",
            "SPAM_MAX_MESSAGES": "",
            "SPAM_WINDOW_SECONDS": "",
        },
        clear=False,
    )
    def test_defaults_when_env_vars_missing(self):
        import importlib
        import config

        env = os.environ.copy()
        env.pop("REPORTS_FOR_BAN", None)
        env.pop("SPAM_MAX_MESSAGES", None)
        env.pop("SPAM_WINDOW_SECONDS", None)
        with patch.dict(os.environ, env, clear=True):
            importlib.reload(config)
            assert config.REPORTS_FOR_BAN == 5
            assert config.SPAM_MAX_MESSAGES == 6
            assert config.SPAM_WINDOW_SECONDS == 3.0
