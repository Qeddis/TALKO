from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

chat_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌍 چت تصادفی")],
        [KeyboardButton(text="👦 چت با پسر")],
        [KeyboardButton(text="👧 چت با دختر")],
        [KeyboardButton(text="⬅️ بازگشت")]
    ],
    resize_keyboard=True
)