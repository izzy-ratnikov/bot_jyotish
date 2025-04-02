from aiogram import types


async def send_long_message(
        message: types.Message,
        text: str,
        max_length: int = 4096,
):
    paragraphs = text.split('\n')
    current_message = ""

    for paragraph in paragraphs:

        if len(current_message) + len(paragraph) + 1 <= max_length:
            current_message += paragraph + "\n"
        else:

            if current_message.strip():
                await message.answer(current_message.strip())
            current_message = paragraph + "\n"

    if current_message.strip():
        await message.answer(current_message.strip())
