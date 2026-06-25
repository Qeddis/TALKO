from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select

from database.db import SessionLocal
from database.models import User
from keyboards.profile import profile_menu
from keyboards.menu import main_menu

router = Router()

waiting_age = set()
waiting_gender = set()
waiting_country = set()
waiting_bio = set()


@router.message(F.text == "👤 پروفایل")
async def profile(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            return

        text = (
            f"👤 پروفایل شما\n\n"
            f"🎂 سن: {user.age or 'ثبت نشده'}\n"
            f"🚻 جنسیت: {user.gender or 'ثبت نشده'}\n"
            f"🌍 کشور: {user.country or 'ثبت نشده'}\n"
            f"📝 بیو:\n{user.bio or 'ثبت نشده'}"
        )

        await message.answer(
            text,
            reply_markup=profile_menu
        )


@router.message(F.text == "⬅️ بازگشت")
async def back(message: Message):
    await message.answer(
        "🏠 منوی اصلی",
        reply_markup=main_menu
    )


@router.message(F.text == "✏️ ثبت سن")
async def ask_age(message: Message):
    waiting_age.add(message.from_user.id)
    await message.answer("🎂 سن خود را وارد کنید:")


@router.message(F.text == "✏️ ثبت جنسیت")
async def ask_gender(message: Message):
    waiting_gender.add(message.from_user.id)
    await message.answer("🚻 جنسیت خود را وارد کنید (پسر یا دختر):")


@router.message(F.text == "✏️ ثبت کشور")
async def ask_country(message: Message):
    waiting_country.add(message.from_user.id)
    await message.answer("🌍 کشور خود را وارد کنید:")


@router.message(F.text == "✏️ ثبت بیو")
async def ask_bio(message: Message):
    waiting_bio.add(message.from_user.id)
    await message.answer("📝 بیو خود را وارد کنید:")


@router.message()
async def save_profile(message: Message):
    user_id = message.from_user.id

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == user_id
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            return

        if user_id in waiting_age:
            waiting_age.remove(user_id)

            try:
                user.age = int(message.text)
            except:
                await message.answer("❌ فقط عدد وارد کنید.")
                return

            await session.commit()
            await message.answer("✅ سن ذخیره شد.")
            return

        if user_id in waiting_gender:
            waiting_gender.remove(user_id)

            user.gender = message.text
            await session.commit()

            await message.answer("✅ جنسیت ذخیره شد.")
            return

        if user_id in waiting_country:
            waiting_country.remove(user_id)

            user.country = message.text
            await session.commit()

            await message.answer("✅ کشور ذخیره شد.")
            return

        if user_id in waiting_bio:
            waiting_bio.remove(user_id)

            user.bio = message.text
            await session.commit()

            await message.answer("✅ بیو ذخیره شد.")
            return