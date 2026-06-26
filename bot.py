import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database.db import init_db
from handlers.admin import router as admin_router
from handlers.chat import router as chat_router
from handlers.gender_search import router as gender_router
from handlers.group import router as group_router
from handlers.help import router as help_router
from handlers.menu import router as menu_router
from handlers.profile import router as profile_router
from handlers.search import router as search_router
from handlers.start import router as start_router
from handlers.referral import router as referral_router
from handlers.vip import router as vip_router
from middleware.banned import BannedMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def setup_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="شروع ربات"),
            BotCommand(command="help", description="راهنما"),
            BotCommand(command="rules", description="قوانین"),
        ]
    )


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set in .env")

    await init_db()

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.message.middleware(BannedMiddleware())

    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(admin_router)
    dp.include_router(vip_router)
    dp.include_router(referral_router)
    dp.include_router(profile_router)
    dp.include_router(menu_router)
    dp.include_router(group_router)
    dp.include_router(search_router)
    dp.include_router(gender_router)
    dp.include_router(chat_router)

    await setup_bot_commands(bot)
    logger.info("TALKO bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
