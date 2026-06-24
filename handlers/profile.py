from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select

from database.db import SessionLocal
from database.models import User

router = Router()


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
            await message.answer("❌ پروفایل پیدا نشد.")
            return

        text = (
            f"👤 پروفایل شما\n\n"
            f"🎂 سن: {user.age or 'ثبت نشده'}\n"
            f"🚻 جنسیت: {user.gender or 'ثبت نشده'}\n"
            f"🌍 کشور: {user.country or 'ثبت نشده'}\n"
            f"📝 بیو:\n{user.bio or 'ثبت نشده'}\n\n"
            "برای ثبت اطلاعات:\n"
            "سن: /age 18\n"
            "جنسیت: /gender پسر\n"
            "کشور: /country ایران\n"
            "بیو: /bio سلام من گیمرم 🎮"
        )

        await message.answer(text)


@router.message(F.text.startswith("/age "))
async def set_age(message: Message):
    try:
        age = int(message.text.replace("/age ", ""))
    except:
        await message.answer("❌ سن باید عدد باشد.")
        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )
        user = result.scalar_one_or_none()

        if user:
            user.age = age
            await session.commit()

    await message.answer("✅ سن ذخیره شد.")


@router.message(F.text.startswith("/gender "))
async def set_gender(message: Message):
    gender = message.text.replace("/gender ", "")

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )
        user = result.scalar_one_or_none()

        if user:
            user.gender = gender
            await session.commit()

    await message.answer("✅ جنسیت ذخیره شد.")


@router.message(F.text.startswith("/country "))
async def set_country(message: Message):
    country = message.text.replace("/country ", "")

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )
        user = result.scalar_one_or_none()

        if user:
            user.country = country
            await session.commit()

    await message.answer("✅ کشور ذخیره شد.")


@router.message(F.text.startswith("/bio "))
async def set_bio(message: Message):
    bio = message.text.replace("/bio ", "")

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )
        user = result.scalar_one_or_none()

        if user:
            user.bio = bio
            await session.commit()

    await message.answer("✅ بیو ذخیره شد.")