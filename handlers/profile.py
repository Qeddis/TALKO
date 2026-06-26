from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select

from database.db import SessionLocal
from database.models import User
from keyboards.edit_profile_menu import edit_profile_menu
from keyboards.profile_menu import profile_menu

router = Router()

MAX_COUNTRY_LENGTH = 50
MAX_BIO_LENGTH = 300

waiting_age: dict[int, float] = {}
waiting_gender: dict[int, float] = {}
waiting_country: dict[int, float] = {}
waiting_bio: dict[int, float] = {}

_EDIT_TIMEOUT = 300  # 5 minutes


def _prune_stale() -> None:
    from time import time

    now = time()
    for store in (waiting_age, waiting_gender, waiting_country, waiting_bio):
        stale = [uid for uid, ts in store.items() if now - ts > _EDIT_TIMEOUT]
        for uid in stale:
            del store[uid]


def is_editing_profile(message: Message) -> bool:
    _prune_stale()
    user_id = message.from_user.id
    return (
        user_id in waiting_age
        or user_id in waiting_gender
        or user_id in waiting_country
        or user_id in waiting_bio
    )


@router.message(F.text == "👤 پروفایل")
async def open_profile_menu(message: Message):
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
    await message.answer("✏️ ویرایش پروفایل", reply_markup=edit_profile_menu)


@router.message(F.text == "🎂 ثبت سن")
async def ask_age(message: Message):
    from time import time

    waiting_age[message.from_user.id] = time()
    await message.answer("🎂 سن خود را وارد کنید:")


@router.message(F.text == "🚻 ثبت جنسیت")
async def ask_gender(message: Message):
    from time import time

    waiting_gender[message.from_user.id] = time()
    await message.answer("🚻 جنسیت خود را وارد کنید:\nپسر یا دختر")


@router.message(F.text == "🌍 ثبت کشور")
async def ask_country(message: Message):
    from time import time

    waiting_country[message.from_user.id] = time()
    await message.answer(f"🌍 کشور خود را وارد کنید (حداکثر {MAX_COUNTRY_LENGTH} کاراکتر):")


@router.message(F.text == "📝 ثبت بیو")
async def ask_bio(message: Message):
    from time import time

    waiting_bio[message.from_user.id] = time()
    await message.answer(f"📝 بیو خود را وارد کنید (حداکثر {MAX_BIO_LENGTH} کاراکتر):")


@router.message(is_editing_profile, F.text)
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

            waiting_age.pop(user_id, None)
            await session.commit()
            await message.answer("✅ سن ذخیره شد.")
            return

        if user_id in waiting_gender:
            gender = message.text.strip()
            if gender not in ("پسر", "دختر"):
                await message.answer("❌ فقط «پسر» یا «دختر» وارد کنید.")
                return

            user.gender = gender
            waiting_gender.pop(user_id, None)
            await session.commit()
            await message.answer("✅ جنسیت ذخیره شد.")
            return

        if user_id in waiting_country:
            country = message.text.strip()
            if len(country) > MAX_COUNTRY_LENGTH:
                await message.answer(
                    f"❌ کشور حداکثر {MAX_COUNTRY_LENGTH} کاراکتر باشد."
                )
                return
            user.country = country
            waiting_country.pop(user_id, None)
            await session.commit()
            await message.answer("✅ کشور ذخیره شد.")
            return

        if user_id in waiting_bio:
            bio = message.text.strip()
            if len(bio) > MAX_BIO_LENGTH:
                await message.answer(
                    f"❌ بیو حداکثر {MAX_BIO_LENGTH} کاراکتر باشد."
                )
                return
            user.bio = bio
            waiting_bio.pop(user_id, None)
            await session.commit()
            await message.answer("✅ بیو ذخیره شد.")
            return
