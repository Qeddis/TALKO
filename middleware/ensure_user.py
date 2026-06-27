from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from database.db import add_user


class EnsureUserMiddleware(BaseMiddleware):
    """Register users on first interaction; /start keeps referral deep-link handling."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            text = event.text or ""
            if not text.startswith("/start"):
                await add_user(
                    telegram_id=event.from_user.id,
                    username=event.from_user.username,
                )
        return await handler(event, data)
