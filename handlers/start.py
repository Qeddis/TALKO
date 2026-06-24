from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.menu import main_menu
from database.db import add_user

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    await add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
    )

    await message.answer(
        "👋 به ربات چت ناشناس خوش آمدی",
        reply_markup=main_menu
    )