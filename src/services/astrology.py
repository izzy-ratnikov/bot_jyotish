import matplotlib.pyplot as plt
from datetime import datetime

import numpy as np
from timezonefinder import TimezoneFinder
import swisseph as swe
import io
from pytz import timezone, utc
from geopy import Nominatim


async def calculate_planet_positions(birth_date, birth_time, location):
    swe.set_ephe_path('.')
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # Определение координат для указанной локации
    geolocator = Nominatim(user_agent="astro_bot")
    loc = geolocator.geocode(location)
    if not loc:
        raise ValueError(f"Локация '{location}' не найдена.")
    latitude, longitude = loc.latitude, loc.longitude

    print(f"Координаты для '{location}': Широта: {latitude}, Долгота: {longitude}")

    # Определяем часовой пояс для локации
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=latitude, lng=longitude)
    if not tz_name:
        raise ValueError(f"Не удалось определить часовой пояс для локации '{location}'.")
    local_tz = timezone(tz_name)

    # Конвертация времени рождения в UTC
    birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%d-%m-%Y %H:%M:%S")
    local_datetime = local_tz.localize(birth_datetime)
    utc_datetime = local_datetime.astimezone(utc)

    julian_day = swe.julday(
        utc_datetime.year, utc_datetime.month, utc_datetime.day,
        utc_datetime.hour + utc_datetime.minute / 60 + utc_datetime.second / 3600
    )

    # Устанавливаем топоцентрические координаты
    elevation = 0  # Можно получить из внешнего API
    swe.set_topo(longitude, latitude, elevation)

    planets = [
        (swe.SUN, "Su"),
        (swe.MOON, "Mo"),
        (swe.MARS, "Ma"),
        (swe.VENUS, "Ve"),
        (swe.MERCURY, "Me"),
        (swe.JUPITER, "Jp"),
        (swe.SATURN, "Sa"),
        (swe.TRUE_NODE, "Ra"),
        (swe.TRUE_NODE, "Ke")
    ]

    zodiac_names = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
    zodiac_signs = {}
    positions = []

    rahu_position = None
    ketu_position = None

    for planet, symbol in planets:
        position, _ = swe.calc_ut(julian_day, planet, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        longitude = position[0]

        # Специальная обработка для Раху и Кету
        if symbol == "Ra":  # Раху
            rahu_position = longitude
            continue
        elif symbol == "Ke":  # Кету
            ketu_position = longitude
            continue

        # Для остальных планет вычисляем положение как обычно
        zodiac_index = int(longitude // 30)  # Индекс знака (каждый знак - 30 градусов)
        zodiac_sign = zodiac_names[zodiac_index]
        degree = int(longitude % 30)  # Оставшиеся градусы в знаке
        minutes = int((longitude % 1) * 60)  # Минуты
        seconds = int(((longitude % 1) * 60 % 1) * 60)  # Секунды

        # Сохраняем позицию и знак с градусами
        positions.append((symbol, longitude))
        zodiac_signs[symbol] = (zodiac_sign, degree, minutes, seconds)

    # Теперь корректируем расположение Раху и Кету
    if rahu_position is not None and ketu_position is not None:
        # Сдвигаем Кету на 180 градусов относительно Раху
        ketu_position = (rahu_position + 180) % 360

        # Добавляем Раху и Кету в список позиций и знаков
        positions.append(("Ra", rahu_position))
        positions.append(("Ke", ketu_position))

        # Вычисляем знаки для Раху и Кету
        for symbol, position in [("Ra", rahu_position), ("Ke", ketu_position)]:
            zodiac_index = int(position // 30)
            zodiac_sign = zodiac_names[zodiac_index]
            degree = int(position % 30)
            minutes = int((position % 1) * 60)
            seconds = int(((position % 1) * 60 % 1) * 60)

            zodiac_signs[symbol] = (zodiac_sign, degree, minutes, seconds)

    return positions, zodiac_signs


async def calculate_asc(birth_date, birth_time, location):
    swe.set_ephe_path('.')
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    geolocator = Nominatim(user_agent="astro_bot")
    loc = geolocator.geocode(location)
    if not loc:
        raise ValueError(f"Локация '{location}' не найдена.")
    latitude, longitude = loc.latitude, loc.longitude

    print(f"Координаты для '{location}': Широта: {latitude}, Долгота: {longitude}")

    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=latitude, lng=longitude)
    if not tz_name:
        raise ValueError(f"Не удалось определить часовой пояс для локации '{location}'.")
    local_tz = timezone(tz_name)

    birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%d-%m-%Y %H:%M:%S")
    local_datetime = local_tz.localize(birth_datetime)
    utc_datetime = local_datetime.astimezone(utc)

    julian_day = swe.julday(
        utc_datetime.year, utc_datetime.month, utc_datetime.day,
        utc_datetime.hour + utc_datetime.minute / 60 + utc_datetime.second / 3600
    )

    elevation = 0
    swe.set_topo(longitude, latitude, elevation)

    zodiac_names = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
    zodiac_signs = {}
    positions = []

    house_positions = swe.houses(julian_day, latitude, longitude, b'P')
    asc_position = house_positions[0][0]

    zodiac_index = int(asc_position // 30)
    zodiac_sign = zodiac_names[zodiac_index]
    degree = int(asc_position % 30)
    minutes = int((asc_position % 1) * 60)
    seconds = int(((asc_position % 1) * 60 % 1) * 60)

    positions.append(("Asc", asc_position))
    zodiac_signs["Asc"] = (zodiac_sign, degree, minutes, seconds)

    return positions, zodiac_signs


async def draw_south_indian_chart(planets):
    fig, ax = plt.subplots(figsize=(8, 8))
    outer_size = 4
    mid = outer_size / 2

    # Рисуем базовую структуру
    ax.plot([0, outer_size], [0, 0], 'k-', linewidth=1)
    ax.plot([0, outer_size], [outer_size, outer_size], 'k-', linewidth=1)
    ax.plot([0, 0], [0, outer_size], 'k-', linewidth=1)
    ax.plot([outer_size, outer_size], [0, outer_size], 'k-', linewidth=1)

    ax.plot([0, outer_size], [0, outer_size], 'k-', linewidth=1)
    ax.plot([0, outer_size], [outer_size, 0], 'k-', linewidth=1)

    ax.plot([0, mid], [mid, outer_size], 'k-', linewidth=1)
    ax.plot([mid, outer_size], [outer_size, mid], 'k-', linewidth=1)
    ax.plot([outer_size, mid], [mid, 0], 'k-', linewidth=1)
    ax.plot([mid, 0], [0, mid], 'k-', linewidth=1)

    # Определяем координаты для размещения планет и асцендента
    def get_position(degree):
        angle = (degree / 360) * 2 * np.pi  # Преобразуем в радианы
        x = mid + (outer_size / 2 - 0.2) * np.cos(angle)  # 0.2 для отступа от центра
        y = mid + (outer_size / 2 - 0.2) * np.sin(angle)
        return x, y

    # Размещаем планеты
    for symbol, longitude in planets:
        zodiac_index = int(longitude // 30)
        degree = longitude % 30
        # Преобразуем в градусы для отображения
        position_degree = zodiac_index * 30 + degree
        x, y = get_position(position_degree)
        ax.text(x, y, symbol, fontsize=18, ha='center', va='center', color='black', fontweight='bold')

    for house_number in range(1, 13):
        house_position = (house_number - 1) * 30 + 40  # Смещаем на 60 градусов вперед
        x, y = get_position(house_position)

        # Смещаем текст к центру квадрата
        x_offset = 0.15 * np.cos((house_position / 360) * 2 * np.pi)
        y_offset = 0.15 * np.sin((house_position / 360) * 2 * np.pi)

        ax.text(x - x_offset, y - y_offset, str(house_number), fontsize=10, ha='center', va='center', color='black')

    ax.set_xlim(-0.5, outer_size + 0.5)
    ax.set_ylim(-0.5, outer_size + 0.5)
    ax.set_aspect('equal')
    ax.axis('off')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    buf.seek(0)

    return buf
