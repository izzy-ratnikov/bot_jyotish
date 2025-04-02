from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Рассчитать карту Джйотиш")]
    ],
    resize_keyboard=True
)

retry_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Рассчитать ещё")]
    ],
    resize_keyboard=True
)

def replace_yo_with_e(text: str):
    return text.replace("ё", "е").replace("Ё", "Е")