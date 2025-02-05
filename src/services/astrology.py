import matplotlib.pyplot as plt
from datetime import datetime

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

    # Знаки зодиака
    zodiac_names = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
    zodiac_signs = {}
    positions = []

    # Получаем позиции домов
    house_positions = swe.houses(julian_day, latitude, longitude, b'P')
    asc_position = house_positions[0][0] - 23.8
    asc_position = asc_position % 360

    zodiac_index = int(asc_position // 30)
    zodiac_sign = zodiac_names[zodiac_index]

    degree = int(asc_position % 30)
    minutes = int((asc_position % 1) * 60)
    seconds = int(((asc_position % 1) * 60 % 1) * 60)

    positions.append(("Asc", asc_position))
    zodiac_signs["Asc"] = (zodiac_sign, degree, minutes, seconds)

    return positions, zodiac_signs


async def draw_north_indian_chart(ascendant_sign):
    fig, ax = plt.subplots(figsize=(8, 8))

    outer_size = 410

    square = plt.Rectangle((5, 5), 410, 410, edgecolor='black', facecolor='black', linewidth=3)
    ax.add_patch(square)

    polygons = {
        "tanbhav": [(210, 10), (110, 110), (210, 210), (310, 110)],
        "dhanbhav": [(10, 10), (210, 10), (110, 110)],
        "anujbhav": [(10, 10), (10, 210), (110, 110)],
        "maatabhav": [(110, 110), (10, 210), (110, 310), (210, 210)],
        "santanbhav": [(10, 210), (110, 310), (10, 410)],
        "rogbhav": [(210, 410), (110, 310), (10, 410)],
        "dampathyabhav": [(210, 410), (110, 310), (210, 210), (310, 310)],
        "aayubhav": [(210, 410), (310, 310), (410, 410)],
        "bhagyabhav": [(310, 310), (410, 410), (410, 210)],
        "karmabhav": [(310, 310), (410, 210), (310, 110), (210, 210)],
        "laabbhav": [(410, 210), (310, 110), (410, 10)],
        "karchbhav": [(310, 110), (410, 10), (210, 10)],
    }

    for points in polygons.values():
        polygon = plt.Polygon(points, edgecolor='black', facecolor='white')
        ax.add_patch(polygon)

    zodiac_coords = [
        {"x": 195, "y": 240},
        {"x": 97, "y": 335},
        {"x": 75, "y": 316},
        {"x": 170, "y": 218},
        {"x": 70, "y": 118},
        {"x": 97, "y": 95},
        {"x": 193, "y": 195},
        {"x": 298, "y": 98},
        {"x": 318, "y": 118},
        {"x": 220, "y": 218},
        {"x": 320, "y": 318},
        {"x": 296, "y": 337}
    ]

    zodiac_signs = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

    ascendant_index = zodiac_signs.index(ascendant_sign)

    for i in range(12):
        sign_index = (ascendant_index + i) % 12
        sign = zodiac_signs[sign_index]
        x = zodiac_coords[i]["x"] + 15
        y = zodiac_coords[i]["y"] - 7
        ax.text(x, y, sign, fontsize=18, ha='center', va='center', color='black', fontweight='bold')

    ax.set_xlim(0, outer_size + 10)
    ax.set_ylim(0, outer_size + 10)
    ax.set_aspect('equal')
    ax.axis('off')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    buf.seek(0)

    return buf
