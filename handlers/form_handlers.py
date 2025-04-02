from datetime import datetime

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from geopy.exc import GeocoderTimedOut
from sqlalchemy.exc import SQLAlchemyError
from geopy import Nominatim
from database.models import Session, UserData
from services.astrology import calculate_planet_positions, draw_north_indian_chart, calculate_asc, get_house_info, \
    calculate_karakas, get_nakshatra_and_pada, get_moon_degree, get_moon_nakshatra
from services.openai import chat_gpt
from utils.chart_data import zodiac_to_number, to_decimal_degrees, zodiac_symbols_to_names, get_starting_planet, \
    calculate_remaining_time, dasha_order, planet_periods
from keyboards.reply import start_keyboard, retry_keyboard, replace_yo_with_e
from utils.message import send_long_message

router = Router()
geolocator = Nominatim(user_agent="jyotish_bot", timeout=10)
CITIES_PER_PAGE = 5


class Form(StatesGroup):
    waiting_for_birth_date = State()
    waiting_for_birth_time = State()
    waiting_for_location = State()
    waiting_for_city_selection = State()


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
        "Пожалуйста, введи свой день рождения (в формате ДД.ММ.ГГГГ).",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(Form.waiting_for_birth_date)


@router.message(Form.waiting_for_birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    birth_date = message.text.strip()
    birth_date = birth_date.replace('.', '-')
    try:
        datetime.strptime(birth_date, "%d-%m-%Y")
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ДД-ММ-ГГГГ или ДД.ММ.ГГГГ")
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
    await message.answer("Теперь введи свое место рождения (город или координаты).")
    await state.set_state(Form.waiting_for_location)


@router.message(Form.waiting_for_location)
async def process_location(message: types.Message, state: FSMContext):
    user_input = message.text.strip()
    if len(user_input) < 2:
        await message.answer("Не удалось распознать локацию. Пожалуйста, введите название города.")
        return

    try:
        locations = geolocator.geocode(user_input, exactly_one=False, limit=52, language="ru")
        if not locations:
            await message.answer("Город не найден. Пожалуйста, попробуйте еще раз.")
            return

        exact_match_found = False
        for location in locations:
            city_name = location.address.split(",")[0].strip()
            if replace_yo_with_e(user_input.lower()) == replace_yo_with_e(city_name.lower()):
                exact_match_found = True
                break

        if not exact_match_found:
            await message.answer("Город не найден. Пожалуйста, введите полное название города.")
            return

        unique_locations = []
        seen_cities = set()
        for location in locations:
            city_name = location.address.split(",")[0].strip()
            region = location.address.split(",")[2].strip() if len(location.address.split(",")) > 2 else ""
            country = location.address.split(",")[-1].strip()

            city_id = f"{city_name}, {region}, {country}"

            if city_id not in seen_cities:
                seen_cities.add(city_id)
                unique_locations.append(location)

        unique_locations.sort(key=lambda loc: loc.address.split(",")[-1].strip())

        await state.update_data(all_locations=unique_locations, page=0)

        await show_city_page(message, state)

    except GeocoderTimedOut:
        await message.answer("Сервис геокодирования временно недоступен. Пожалуйста, попробуйте позже.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при поиске города: {e}")


async def show_city_page(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    all_locations = user_data.get("all_locations")
    page = user_data.get("page", 0)

    start_index = page * CITIES_PER_PAGE
    end_index = start_index + CITIES_PER_PAGE
    current_locations = all_locations[start_index:end_index]

    builder = InlineKeyboardBuilder()
    for location in current_locations:

        address_parts = location.address.split(",")
        city_name = address_parts[0].strip()
        country = address_parts[-1].strip()

        if len(address_parts) > 2:
            region = address_parts[2].strip()
            if region and region != country:
                button_text = f"{city_name}, {region}, {country}"
            else:
                button_text = f"{city_name}, {country}"
        else:
            button_text = f"{city_name}, {country}"

        callback_data = f"city_{location.latitude}_{location.longitude}"
        builder.add(types.InlineKeyboardButton(text=button_text, callback_data=callback_data))

    if page > 0:
        builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_page"))
    if end_index < len(all_locations):
        builder.add(types.InlineKeyboardButton(text="➡️ Вперед", callback_data="next_page"))

    builder.adjust(1)
    await message.answer("Выберите город из списка:", reply_markup=builder.as_markup())


@router.callback_query(lambda c: c.data in ["prev_page", "next_page"])
async def process_page_navigation(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    page = user_data.get("page", 0)

    if callback_query.data == "prev_page":
        page -= 1
    elif callback_query.data == "next_page":
        page += 1

    await state.update_data(page=page)

    await show_city_page(callback_query.message, state)
    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith('city_'))
async def process_city_selection(callback_query: types.CallbackQuery, state: FSMContext):
    _, latitude, longitude = callback_query.data.split('_')
    city_coords = (float(latitude), float(longitude))

    try:
        location = geolocator.reverse(city_coords, exactly_one=True, language="ru")
        city_address = location.address
    except Exception as e:
        await callback_query.message.answer(f"Не удалось получить адрес города: {e}")
        return

    await state.update_data(location=city_address)
    await confirm_and_proceed(callback_query.message, state)


async def confirm_and_proceed(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    birth_date = user_data.get('birth_date')
    birth_time = user_data.get('birth_time')
    location = user_data.get('location')

    if not birth_date or not birth_time or not location:
        await message.answer("Не указаны дата или время рождения. Пожалуйста, попробуйте снова.")
        return

    try:
        await calculate_and_send_chart(message, user_data)
        await state.clear()
    except ValueError as e:
        await message.answer(
            f"Локация введена некорректно. Пожалуйста, введите корректные координаты или название города. {e}")


async def save_user_data(message: types.Message, user_data: dict, interpretation: str = None,
                         zodiac_info: str = None, houses_info: str = None, vimshottari_dasha: str = None):
    session = Session()
    try:
        user_data_entry = UserData(
            telegram_id=message.chat.id,
            username=message.chat.username,
            location=user_data['location'],
            birth_date=datetime.strptime(user_data['birth_date'], "%d-%m-%Y").date(),
            birth_time=datetime.strptime(user_data['birth_time'], "%H:%M:%S").time(),
            chart_interpretation=interpretation,
            zodiac_info=zodiac_info,
            houses_info=houses_info,
            vimshottari_dasha=vimshottari_dasha
        )
        session.add(user_data_entry)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        await message.answer(f"Ошибка сохранения данных: {str(e)}")
    finally:
        session.close()


async def calculate_and_send_chart(message: types.Message, user_data: dict):
    birth_date = user_data['birth_date']
    birth_time = user_data['birth_time']
    location = user_data['location']

    planets_positions, zodiac_signs = await calculate_planet_positions(birth_date, birth_time, location)
    karakas = await calculate_karakas(planets_positions)
    asc_positions, asc_zodiac_signs = await calculate_asc(birth_date, birth_time, location)

    ascendant_info = asc_zodiac_signs.get("Asc")
    if not ascendant_info:
        await message.answer("Ошибка: Не удалось получить информацию об асценденте.")
        return

    asc_sign, asc_deg, asc_min, asc_sec = ascendant_info
    asc_longitude = to_decimal_degrees(asc_deg, asc_min, asc_sec)
    asc_nakshatra, asc_pada = await get_nakshatra_and_pada(zodiac_symbols_to_names.get(asc_sign, asc_sign),
                                                           asc_longitude)
    ascendant_string = f"Asc {asc_sign} {asc_deg}˚{asc_min:02d}'{asc_sec:02d}\"   {asc_nakshatra} {asc_pada}"

    asc_sign_number = zodiac_to_number.get(asc_sign)
    if not asc_sign_number:
        await message.answer("Ошибка: Не удалось определить номер знака зодиака для асцендента.")
        return

    house_info = await get_house_info(asc_sign, planets_positions)

    chart_image = await draw_north_indian_chart(asc_sign_number, planets_positions)
    input_file = BufferedInputFile(chart_image.read(), filename="chart.png")
    await message.answer_photo(photo=input_file, caption="Ваш South Indian Chart.")

    karakas_by_planet = {v: k for k, v in karakas.items()}

    zodiac_info = "\n".join([
        f"{symbol:<3} {karakas_by_planet.get(symbol, ' '):<5} {zodiac_sign} {degree:>2}˚{minutes:02d}'{seconds:02d}\"   {nakshatra} {pada}"
        if karakas_by_planet.get(symbol) else
        f"{symbol:<3} {zodiac_sign} {degree:>2}˚{minutes:02d}'{seconds:02d}\"   {nakshatra} {pada}"
        for symbol, (zodiac_sign, degree, minutes, seconds) in zodiac_signs.items()
        if (nakshatra := (await get_nakshatra_and_pada(zodiac_symbols_to_names.get(zodiac_sign, zodiac_sign),
                                                       to_decimal_degrees(degree, minutes, seconds)))[0]) and
           (pada := (await get_nakshatra_and_pada(zodiac_symbols_to_names.get(zodiac_sign, zodiac_sign),
                                                  to_decimal_degrees(degree, minutes, seconds)))[1])
    ])
    house_info_text = "Дома в карте:\n" + "\n".join(house_info)

    moon_nakshatra = await get_moon_nakshatra(planets_positions)
    starting_planet = get_starting_planet(moon_nakshatra)
    moon_degree = await get_moon_degree(planets_positions)
    years_remaining, years_passed = calculate_remaining_time(moon_degree, starting_planet)
    start_index = dasha_order.index(starting_planet)
    sequence = dasha_order[start_index:] + dasha_order[:start_index]
    vimshottari_dasha = "Последовательность периодов\n"

    for i, planet in enumerate(sequence):
        if i == 0:
            vimshottari_dasha += f"▸ {planet}: {years_remaining:.2f} лет\n"
        else:
            vimshottari_dasha += f"▸ {planet}: {planet_periods[planet]} лет\n"
    vimshottari_dasha += f"▸ {starting_planet}: {years_passed:.2f} лет\n"
    vimshottari_dasha += "Общая продолжительность: 120 лет"
    interpretation = await chat_gpt(house_info_text, vimshottari_dasha)
    await save_user_data(
        message,
        user_data,
        interpretation=interpretation,
        zodiac_info=zodiac_info,
        houses_info=house_info_text,
        vimshottari_dasha=vimshottari_dasha
    )
    await message.answer(vimshottari_dasha)
    await message.answer(f"Знаки зодиака с градусами:\n{zodiac_info}\n{ascendant_string}")
    await message.answer(house_info_text)

    processing_message = await message.answer("Обрабатываем результаты расчета...")

    await processing_message.delete()
    await send_long_message(message, f"Расшифровка натальной карты:\n{interpretation}")

    await message.answer(
        "Если хотите рассчитать новую карту, нажмите на кнопку ниже.",
        reply_markup=retry_keyboard
    )


@router.message(lambda message: message.text == "Рассчитать ещё")
async def retry_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await get_user_data(message, state)
