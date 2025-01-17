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

    # Координаты для каждого дома в South Indian Chart
    house_positions = {
        1: (outer_size * 3 / 4, outer_size * 3 / 4),
        2: (outer_size / 2, outer_size * 3 / 4),
        3: (outer_size / 4, outer_size * 3 / 4),
        4: (outer_size / 4, outer_size / 2),
        5: (outer_size / 4, outer_size / 4),
        6: (outer_size / 2, outer_size / 4),
        7: (outer_size * 3 / 4, outer_size / 4),
        8: (outer_size * 3 / 4, outer_size / 2),
        9: (outer_size / 2, outer_size / 2),
        10: (outer_size / 2, outer_size / 4),
        11: (outer_size / 4, outer_size / 2),
        12: (outer_size * 3 / 4, outer_size / 4),
    }

    # Группируем планеты по домам
    house_planets = {i: [] for i in range(1, 13)}  # Инициализируем словарь для планет в домах
    for planet, position in planets:
        house = int(position / 30) + 1  # Определяем дом
        house_planets[house].append(planet)

    # Размещаем планеты с корректировкой позиций
    for house, planet_list in house_planets.items():
        base_x, base_y = house_positions.get(house, (mid, mid))  # Центр дома
        for i, planet in enumerate(planet_list):
            # Смещения для планет внутри дома
            offset_x = (i % 3 - 1) * 0.2  # Горизонтальное смещение
            offset_y = (i // 3 - 1) * 0.2  # Вертикальное смещение
            ax.text(
                base_x + offset_x, base_y + offset_y, planet,
                fontsize=16, ha='center', va='center', color='black', fontweight='bold'
            )

    plt.axis('equal')
    plt.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf
