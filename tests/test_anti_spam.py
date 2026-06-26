from unittest.mock import patch
from time import time

from services.anti_spam import is_spam, _timestamps


class TestIsSpam:
    def setup_method(self):
        _timestamps.clear()

    @patch("services.anti_spam.SPAM_MAX_MESSAGES", 3)
    @patch("services.anti_spam.SPAM_WINDOW_SECONDS", 2.0)
    def test_not_spam_below_threshold(self):
        user_id = 100
        assert is_spam(user_id) is False
        assert is_spam(user_id) is False
        assert is_spam(user_id) is False

    @patch("services.anti_spam.SPAM_MAX_MESSAGES", 3)
    @patch("services.anti_spam.SPAM_WINDOW_SECONDS", 2.0)
    def test_spam_above_threshold(self):
        user_id = 200
        assert is_spam(user_id) is False
        assert is_spam(user_id) is False
        assert is_spam(user_id) is False
        assert is_spam(user_id) is True

    @patch("services.anti_spam.SPAM_MAX_MESSAGES", 3)
    @patch("services.anti_spam.SPAM_WINDOW_SECONDS", 2.0)
    def test_different_users_independent(self):
        user_a = 300
        user_b = 400
        for _ in range(3):
            is_spam(user_a)
        assert is_spam(user_b) is False

    @patch("services.anti_spam.SPAM_MAX_MESSAGES", 3)
    @patch("services.anti_spam.SPAM_WINDOW_SECONDS", 0.0)
    def test_messages_outside_window_not_spam(self):
        user_id = 500
        _timestamps[user_id] = [time() - 100, time() - 99, time() - 98]
        assert is_spam(user_id) is False

    @patch("services.anti_spam.SPAM_MAX_MESSAGES", 3)
    @patch("services.anti_spam.SPAM_WINDOW_SECONDS", 2.0)
    def test_old_messages_pruned_after_60s(self):
        user_id = 600
        _timestamps[user_id] = [time() - 120, time() - 100, time() - 80]
        assert is_spam(user_id) is False
        assert len(_timestamps[user_id]) == 1

    @patch("services.anti_spam.SPAM_MAX_MESSAGES", 1)
    @patch("services.anti_spam.SPAM_WINDOW_SECONDS", 5.0)
    def test_single_message_threshold(self):
        user_id = 700
        assert is_spam(user_id) is False
        assert is_spam(user_id) is True

    @patch("services.anti_spam.SPAM_MAX_MESSAGES", 6)
    @patch("services.anti_spam.SPAM_WINDOW_SECONDS", 3.0)
    def test_default_config_values(self):
        user_id = 800
        for _ in range(6):
            assert is_spam(user_id) is False
        assert is_spam(user_id) is True
