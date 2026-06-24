from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "👤 پروفایل")
async def profile(message: Message):
    await message.answer("✅ دکمه پروفایل کار می‌کند")