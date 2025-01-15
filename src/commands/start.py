from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from src.handlers.form_handlers import Form
from aiogram.filters import Command


router = Router()

# @router.message(Command("start"))
# async def get_user_data(message: types.Message, state: FSMContext):
#     await message.answer(
#         "Привет! Я астрологический бот. Пожалуйста, введи свой день рождения (в формате ГГГГ-ММ-ДД)."
#     )
#     await state.set_state(Form.waiting_for_birth_date)

