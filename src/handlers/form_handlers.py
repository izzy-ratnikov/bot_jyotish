from datetime import datetime

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from aiogram.fsm.state import State, StatesGroup
from src.services.astrology import build_astrological_chart

router = Router()


class Form(StatesGroup):
    waiting_for_birth_date = State()
    waiting_for_birth_time = State()
    waiting_for_location = State()


@router.message(Command("start"))
async def get_user_data(message: types.Message, state: FSMContext):
    await message.answer("Привет! Я астрологический бот. Пожалуйста, введи свой день рождения (в формате ГГГГ-ММ-ДД).")
    await state.set_state(Form.waiting_for_birth_date)


@router.message(Form.waiting_for_birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    birth_date = message.text.strip()
    try:
        datetime.strptime(birth_date, "%Y-%m-%d")
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")
        return

    await state.update_data(birth_date=birth_date)
    await message.answer("Отлично! Теперь, пожалуйста, введи время рождения (в формате ЧЧ:ММ:СС).")
    await state.set_state(Form.waiting_for_birth_time)


@router.message(Form.waiting_for_birth_time)
async def process_birth_time(message: types.Message, state: FSMContext):
    birth_time = message.text.strip()
    try:
        datetime.strptime(birth_time, "%H:%M:%S")
    except ValueError:
        await message.answer("Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ:СС.")
        return

    await state.update_data(birth_time=birth_time)
    await message.answer("Теперь введи свою локацию (город или координаты).")
    await state.set_state(Form.waiting_for_location)


@router.message(Form.waiting_for_location)
async def process_location(message: types.Message, state: FSMContext):
    location = message.text.strip()
    # Простая проверка (опционально, можно улучшить)
    if len(location) < 2:
        await message.answer("Не удалось распознать локацию. Пожалуйста, введите координаты или название города.")
        return

    await state.update_data(location=location)
    user_data = await state.get_data()

    # Генерация астрологической карты
    coordinates, chart_image = await build_astrological_chart(
        user_data['birth_date'], user_data['birth_time'], user_data['location']
    )

    input_file = BufferedInputFile(chart_image.read(), filename="chart.png")
    await message.answer_photo(photo=input_file, caption=f"Ваш South Indian Chart. Локация: {coordinates}")
    await state.clear()

