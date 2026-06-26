from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

vip_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 خرید VIP با سکه")],
        [KeyboardButton(text="⭐ خرید VIP با استار")],
        [KeyboardButton(text="⬅️ بازگشت")],
    ],
    resize_keyboard=True,
)
