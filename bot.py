import asyncio

from aiogram import Bot
from aiogram import Dispatcher

from config import BOT_TOKEN

from database.db import init_db

from handlers.start import router as start_router

from handlers.search import router as search_router

from handlers.chat import router as chat_router

from handlers.profile import router as profile_router

from handlers.gender_search import router as gender_router

async def main():

    await init_db()

    bot = Bot(BOT_TOKEN)

    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(search_router)
    dp.include_router(chat_router)
    dp.include_router(gender_router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

