from aiogram import types


async def send_long_message(message: types.Message, text: str, max_length: int = 4096):
    for part in [text[i:i + max_length] for i in range(0, len(text), max_length)]:
        await message.answer(part)
