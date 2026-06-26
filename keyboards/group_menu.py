from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

group_main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌐 اتاق عمومی")],
        [KeyboardButton(text="💎 اتاق VIP")],
        [KeyboardButton(text="⬅️ بازگشت")],
    ],
    resize_keyboard=True,
)

group_chat_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ خروج از اتاق")],
        [KeyboardButton(text="⬅️ بازگشت")],
    ],
    resize_keyboard=True,
)
