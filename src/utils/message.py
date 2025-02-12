from aiogram import types


# async def send_long_message(message: types.Message, text: str, max_length: int = 4096):
#     while text:
#         if len(text) <= max_length:
#             await message.answer(text)
#             break
#
#         split_index = text.rfind(' ', 0, max_length)
#         if split_index == -1:
#             split_index = max_length
#
#         part = text[:split_index]
#         await message.answer(part)
#         text = text[split_index:].lstrip()
async def send_long_message(message: types.Message, text: str, max_length: int = 4096):
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
