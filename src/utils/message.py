from aiogram import types


async def send_long_message(message: types.Message, text: str, max_length: int = 4096):
    if len(text) <= max_length:
        await message.answer(text)
        return

    parts = []
    current_part = ""

    for line in text.split('\n'):
        if len(current_part) + len(line) + 1 <= max_length:
            current_part += line + "\n"
        else:
            if current_part:
                parts.append(current_part.strip())
            current_part = line + "\n"

    if current_part:
        parts.append(current_part.strip())

    for part in parts:
        await message.answer(part)
