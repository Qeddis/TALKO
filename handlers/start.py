from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.menu import main_menu

router = Router()

@router.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "👋 به ربات چت ناشناس خوش آمدی",
        reply_markup=main_menu
    )