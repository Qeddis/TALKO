import asyncio

from aiogram import Bot
from aiogram import Dispatcher

from config import BOT_TOKEN

from database.db import init_db

from handlers.start import router as start_router

async def main():

    await init_db()

    bot = Bot(BOT_TOKEN)

    dp = Dispatcher()

    dp.include_router(start_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

