from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from middleware.banned import BannedMiddleware


@pytest.fixture
def middleware():
    return BannedMiddleware()


@pytest.fixture
def make_event():
    """Factory to create mock Message events."""

    def _make(user_id=12345, text=None):
        from aiogram.types import Message

        event = MagicMock(spec=Message)
        event.from_user = MagicMock()
        event.from_user.id = user_id
        event.text = text
        event.answer = AsyncMock()
        return event

    return _make


class TestBannedMiddleware:
    @patch("middleware.banned.ADMIN_IDS", {999})
    async def test_admin_always_allowed(self, middleware, make_event):
        event = make_event(user_id=999)
        handler = AsyncMock(return_value="ok")
        result = await middleware(handler, event, {})
        handler.assert_called_once_with(event, {})
        assert result == "ok"

    @patch("middleware.banned.ADMIN_IDS", set())
    @patch("middleware.banned.get_user", new_callable=AsyncMock)
    async def test_banned_user_blocked(self, mock_get_user, middleware, make_event):
        user = MagicMock()
        user.banned = True
        mock_get_user.return_value = user

        event = make_event(user_id=100, text="hello")
        handler = AsyncMock()
        result = await middleware(handler, event, {})

        handler.assert_not_called()
        event.answer.assert_called_once()
        assert result is None

    @patch("middleware.banned.ADMIN_IDS", set())
    @patch("middleware.banned.get_user", new_callable=AsyncMock)
    async def test_banned_user_can_send_start(
        self, mock_get_user, middleware, make_event
    ):
        user = MagicMock()
        user.banned = True
        mock_get_user.return_value = user

        event = make_event(user_id=100, text="/start")
        handler = AsyncMock(return_value="started")
        result = await middleware(handler, event, {})

        handler.assert_called_once()
        assert result == "started"

    @patch("middleware.banned.ADMIN_IDS", set())
    @patch("middleware.banned.get_user", new_callable=AsyncMock)
    async def test_non_banned_user_allowed(
        self, mock_get_user, middleware, make_event
    ):
        user = MagicMock()
        user.banned = False
        mock_get_user.return_value = user

        event = make_event(user_id=200)
        handler = AsyncMock(return_value="ok")
        result = await middleware(handler, event, {})

        handler.assert_called_once()
        assert result == "ok"

    @patch("middleware.banned.ADMIN_IDS", set())
    @patch("middleware.banned.get_user", new_callable=AsyncMock)
    async def test_new_user_no_db_record(
        self, mock_get_user, middleware, make_event
    ):
        mock_get_user.return_value = None

        event = make_event(user_id=300)
        handler = AsyncMock(return_value="ok")
        result = await middleware(handler, event, {})

        handler.assert_called_once()
        assert result == "ok"

    @patch("middleware.banned.ADMIN_IDS", set())
    async def test_non_message_event_passes_through(self, middleware):
        event = MagicMock()
        del event.from_user
        event.__class__ = object
        handler = AsyncMock(return_value="ok")
        result = await middleware(handler, event, {})
        handler.assert_called_once()
