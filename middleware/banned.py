from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from config import ADMIN_IDS
from database.db import get_user


class BannedMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            if event.from_user.id in ADMIN_IDS:
                return await handler(event, data)

            user = await get_user(event.from_user.id)
            if user and user.banned:
                if event.text and event.text.startswith("/start"):
                    return await handler(event, data)
                await event.answer("❌ حساب شما مسدود شده است.")
                return None

        return await handler(event, data)
