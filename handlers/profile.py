from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select

from database.db import SessionLocal
from database.models import User
from keyboards.edit_profile_menu import edit_profile_menu
from keyboards.profile_menu import profile_menu

router = Router()

waiting_age: set[int] = set()
waiting_gender: set[int] = set()
waiting_country: set[int] = set()
waiting_bio: set[int] = set()
in_edit_menu: set[int] = set()


def is_in_edit_profile(user_id: int) -> bool:
    return (
        user_id in waiting_age
        or user_id in waiting_gender
        or user_id in waiting_country
        or user_id in waiting_bio
        or user_id in in_edit_menu
    )


def clear_profile_edit(user_id: int) -> None:
    waiting_age.discard(user_id)
    waiting_gender.discard(user_id)
    waiting_country.discard(user_id)
    waiting_bio.discard(user_id)
    in_edit_menu.discard(user_id)


@router.message(F.text == "👤 پروفایل")
async def open_profile_menu(message: Message):
    clear_profile_edit(message.from_user.id)
    await message.answer("👤 منوی پروفایل", reply_markup=profile_menu)


@router.message(F.text == "📄 مشاهده پروفایل")
async def profile(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )

        user = result.scalar_one_or_none()

        if not user:
            await message.answer("❌ پروفایل پیدا نشد.")
            return

        vip_badge = " 💎" if user.vip else ""
        text = (
            f"👤 پروفایل شما{vip_badge}\n\n"
            f"🎂 سن: {user.age or 'ثبت نشده'}\n"
            f"🚻 جنسیت: {user.gender or 'ثبت نشده'}\n"
            f"🌍 کشور: {user.country or 'ثبت نشده'}\n"
            f"📝 بیو:\n{user.bio or 'ثبت نشده'}\n"
            f"🪙 سکه: {user.coins}"
        )

        await message.answer(text)


@router.message(F.text == "✏️ ویرایش پروفایل")
async def edit_profile(message: Message):
    in_edit_menu.add(message.from_user.id)
    await message.answer("✏️ ویرایش پروفایل", reply_markup=edit_profile_menu)


@router.message(F.text == "🎂 ثبت سن")
async def ask_age(message: Message):
    waiting_age.add(message.from_user.id)
    in_edit_menu.add(message.from_user.id)
    await message.answer("🎂 سن خود را وارد کنید:")


@router.message(F.text == "🚻 ثبت جنسیت")
async def ask_gender(message: Message):
    waiting_gender.add(message.from_user.id)
    in_edit_menu.add(message.from_user.id)
    await message.answer("🚻 جنسیت خود را وارد کنید:\nپسر یا دختر")


@router.message(F.text == "🌍 ثبت کشور")
async def ask_country(message: Message):
    waiting_country.add(message.from_user.id)
    in_edit_menu.add(message.from_user.id)
    await message.answer("🌍 کشور خود را وارد کنید:")


@router.message(F.text == "📝 ثبت بیو")
async def ask_bio(message: Message):
    waiting_bio.add(message.from_user.id)
    in_edit_menu.add(message.from_user.id)
    await message.answer("📝 بیو خود را وارد کنید:")


def _is_editing_field(message: Message) -> bool:
    user_id = message.from_user.id
    return (
        user_id in waiting_age
        or user_id in waiting_gender
        or user_id in waiting_country
        or user_id in waiting_bio
    )


def _in_profile_edit_back(message: Message) -> bool:
    return is_in_edit_profile(message.from_user.id)


@router.message(_in_profile_edit_back, F.text == "⬅️ بازگشت")
async def profile_back(message: Message):
    clear_profile_edit(message.from_user.id)
    await message.answer("👤 منوی پروفایل", reply_markup=profile_menu)


@router.message(_is_editing_field, F.text)
async def save_profile(message: Message):
    user_id = message.from_user.id

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )

        user = result.scalar_one_or_none()

        if not user:
            return

        if user_id in waiting_age:
            try:
                age = int(message.text.strip())
                if age < 10 or age > 100:
                    raise ValueError
                user.age = age
            except ValueError:
                await message.answer("❌ سن معتبر وارد کنید (۱۰ تا ۱۰۰).")
                return

            waiting_age.discard(user_id)
            await session.commit()
            await message.answer("✅ سن ذخیره شد.", reply_markup=edit_profile_menu)
            return

        if user_id in waiting_gender:
            gender = message.text.strip()
            if gender not in ("پسر", "دختر"):
                await message.answer("❌ فقط «پسر» یا «دختر» وارد کنید.")
                return

            user.gender = gender
            waiting_gender.discard(user_id)
            await session.commit()
            await message.answer("✅ جنسیت ذخیره شد.", reply_markup=edit_profile_menu)
            return

        if user_id in waiting_country:
            user.country = message.text.strip()
            waiting_country.discard(user_id)
            await session.commit()
            await message.answer("✅ کشور ذخیره شد.", reply_markup=edit_profile_menu)
            return

        if user_id in waiting_bio:
            user.bio = message.text.strip()
            waiting_bio.discard(user_id)
            await session.commit()
            await message.answer("✅ بیو ذخیره شد.", reply_markup=edit_profile_menu)
            return
