from datetime import datetime

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.exc import SQLAlchemyError

from src.database.models.models import Session, UserData
from src.services.astrology import calculate_planet_positions, draw_south_indian_chart
from src.utils.keyboards import start_keyboard, retry_keyboard

router = Router()


class Form(StatesGroup):
    waiting_for_birth_date = State()
    waiting_for_birth_time = State()
    waiting_for_location = State()


@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "Привет! Я астрологический бот. Нажмите кнопку ниже, чтобы рассчитать свою карту Джйотиш.",
        reply_markup=start_keyboard
    )
    await state.clear()


@router.message(lambda message: message.text == "Рассчитать карту Джйотиш")
async def get_user_data(message: types.Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, введи свой день рождения (в формате ДД-ММ-ГГГГ).",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(Form.waiting_for_birth_date)


@router.message(Form.waiting_for_birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    birth_date = message.text.strip()
    try:
        datetime.strptime(birth_date, "%d-%m-%Y")
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ДД-ММ-ГГГГ.")
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
    if len(location) < 2:
        await message.answer("Не удалось распознать локацию. Пожалуйста, введите координаты или название города.")
        return

    await state.update_data(location=location)
    user_data = await state.get_data()
    birth_date = user_data['birth_date']
    birth_time = user_data['birth_time']

    # Сохраняем данные в базу
    session = Session()
    try:
        user_data_entry = UserData(
            telegram_id=message.from_user.id,
            location=location,
            birth_date=datetime.strptime(user_data['birth_date'], "%d-%m-%Y").date(),
            birth_time=datetime.strptime(user_data['birth_time'], "%H:%M:%S").time(),
        )
        session.add(user_data_entry)
        session.commit()
        await message.answer("Данные сохранены в базе данных.")
    except SQLAlchemyError as e:
        session.rollback()
        await message.answer(f"Произошла ошибка при сохранении данных: {str(e)}")
    finally:
        session.close()

    planets_positions, zodiac_signs = await calculate_planet_positions(birth_date, birth_time, location)
    chart_image = await draw_south_indian_chart(planets_positions)

    input_file = BufferedInputFile(chart_image.read(), filename="chart.png")
    await message.answer_photo(photo=input_file, caption=f"Ваш South Indian Chart.")

    # Формируем строку с позициями планет
    zodiac_info = "\n".join([
        f"{symbol} {zodiac_sign} {degree}˚{minutes:02d}'{seconds:02d}\""
        for symbol, (zodiac_sign, degree, minutes, seconds) in zodiac_signs.items()
    ])

    await message.answer(f"Знаки зодиака с градусами:\n{zodiac_info}")
    await message.answer(
        "Если хотите рассчитать новую карту, нажмите на кнопку ниже.",
        reply_markup=retry_keyboard
    )
    await state.clear()


@router.message(lambda message: message.text == "Рассчитать ещё")
async def retry_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await get_user_data(message, state)
