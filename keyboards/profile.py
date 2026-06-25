from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

profile_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ ثبت سن")],
        [KeyboardButton(text="✏️ ثبت جنسیت")],
        [KeyboardButton(text="✏️ ثبت کشور")],
        [KeyboardButton(text="✏️ ثبت بیو")],
        [KeyboardButton(text="⬅️ بازگشت")]
    ],
    resize_keyboard=True
)