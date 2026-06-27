from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

search_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏹ لغو جستجو")],
        [KeyboardButton(text="⬅️ بازگشت")],
    ],
    resize_keyboard=True,
)
