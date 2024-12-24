from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.services.astrology import build_astrological_chart
from src.utils.validators import validate_date, validate_time, validate_location
from aiogram.types import InputFile
router = Router()  # Создаём объект маршрутизатора

class Form(StatesGroup):
    waiting_for_birth_date = State()
    waiting_for_birth_time = State()
    waiting_for_location = State()

@router.message(Form.waiting_for_birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    birth_date = message.text.strip()
    if not validate_date(birth_date):
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")
        return

    await state.update_data(birth_date=birth_date)
    await message.answer("Отлично! Теперь, пожалуйста, введи время рождения (в формате ЧЧ:ММ:СС).")
    await state.set_state(Form.waiting_for_birth_time)

@router.message(Form.waiting_for_birth_time)
async def process_birth_time(message: types.Message, state: FSMContext):
    birth_time = message.text.strip()
    if not validate_time(birth_time):
        await message.answer("Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ:СС.")
        return

    await state.update_data(birth_time=birth_time)
    await message.answer("Теперь введи свою локацию (город или координаты).")
    await state.set_state(Form.waiting_for_location)

@router.message(Form.waiting_for_location)
async def process_location(message: types.Message, state: FSMContext):
    location = message.text.strip()
    if not validate_location(location):
        await message.answer("Не удалось распознать локацию. Пожалуйста, введите координаты (например, 12.3456, 45.6789) или название города.")
        return

    await state.update_data(location=location)
    user_data = await state.get_data()

    # Генерация данных для астрологической карты
    coordinates, chart_image = await build_astrological_chart(
        user_data['birth_date'], user_data['birth_time'], user_data['location']
    )

    # Преобразование BytesIO в InputFile
    chart_image.seek(0)  # Обязательно установите указатель в начало
    input_file = InputFile(chart_image)

    await message.answer(f"Координаты для вашего рождения: {coordinates}")
    await message.answer_photo(photo=input_file, caption="Ваш астрологический график")
    await state.clear()