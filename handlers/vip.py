from aiogram import F, Router
from aiogram.types import (
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

from config import SUPPORT_USERNAME, VIP_COIN_PRICE, VIP_STARS_PRICE
from database.db import activate_vip, get_user, purchase_vip_with_coins
from keyboards.menu import main_menu
from keyboards.vip_menu import vip_menu

router = Router()


def _vip_benefits() -> str:
    return (
        "• اولویت در جفت‌سازی\n"
        "• نشان 💎 در پروفایل\n"
        "• دسترسی به اتاق VIP گروهی"
    )


@router.message(F.text == "💎 VIP")
async def vip_info(message: Message):
    user = await get_user(message.from_user.id)

    if not user:
        await message.answer("❌ پروفایل پیدا نشد.")
        return

    if user.vip:
        await message.answer(
            "💎 شما کاربر VIP هستید!\n\n"
            f"مزایا:\n{_vip_benefits()}\n\n"
            f"🪙 سکه: {user.coins}"
        )
        return

    support = f"\n📞 پشتیبانی: @{SUPPORT_USERNAME}" if SUPPORT_USERNAME else ""
    stars_line = (
        f"⭐ خرید با استار: {VIP_STARS_PRICE} استار\n"
        if VIP_STARS_PRICE > 0
        else ""
    )

    await message.answer(
        "💎 VIP\n\n"
        f"مزایا:\n{_vip_benefits()}\n\n"
        f"🪙 سکه شما: {user.coins}\n"
        f"💳 قیمت با سکه: {VIP_COIN_PRICE} سکه\n"
        f"{stars_line}"
        "یکی از گزینه‌های زیر را انتخاب کنید:"
        f"{support}",
        reply_markup=vip_menu,
    )


@router.message(F.text == "💳 خرید VIP با سکه")
async def buy_vip_coins(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        return

    if user.vip:
        await message.answer("💎 شما از قبل VIP هستید.", reply_markup=main_menu)
        return

    ok, reason = await purchase_vip_with_coins(message.from_user.id)
    if ok:
        user = await get_user(message.from_user.id)
        await message.answer(
            "✅ VIP فعال شد!\n\n"
            f"مزایا:\n{_vip_benefits()}\n\n"
            f"🪙 سکه باقی‌مانده: {user.coins if user else 0}",
            reply_markup=main_menu,
        )
        return

    if reason == "insufficient":
        await message.answer(
            f"❌ سکه کافی ندارید.\n"
            f"نیاز: {VIP_COIN_PRICE} | موجودی: {user.coins}\n\n"
            "از ادمین یا پشتیبانی سکه دریافت کنید.",
            reply_markup=vip_menu,
        )
        return

    await message.answer("❌ خطا در فعال‌سازی VIP.", reply_markup=vip_menu)


@router.message(F.text == "⭐ خرید VIP با استار")
async def buy_vip_stars(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        return

    if user.vip:
        await message.answer("💎 شما از قبل VIP هستید.", reply_markup=main_menu)
        return

    if VIP_STARS_PRICE <= 0:
        await message.answer(
            "❌ پرداخت استار در حال حاضر فعال نیست.",
            reply_markup=vip_menu,
        )
        return

    await message.bot.send_invoice(
        chat_id=message.chat.id,
        title="VIP TALKO",
        description="فعال‌سازی VIP — اولویت جفت‌سازی + اتاق VIP",
        payload=f"vip:{message.from_user.id}",
        currency="XTR",
        prices=[LabeledPrice(label="VIP", amount=VIP_STARS_PRICE)],
        provider_token="",
    )


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    if query.invoice_payload.startswith("vip:"):
        await query.answer(ok=True)
        return
    await query.answer(ok=False, error_message="پرداخت نامعتبر است.")


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    if not payload.startswith("vip:"):
        return

    user_id = int(payload.split(":", 1)[1])
    if user_id != message.from_user.id:
        return

    if await activate_vip(user_id):
        await message.answer(
            "✅ VIP با موفقیت فعال شد!\n\n"
            f"مزایا:\n{_vip_benefits()}",
            reply_markup=main_menu,
        )
