import io
import matplotlib.pyplot as plt
from datetime import datetime
import swisseph as swe


async def calculate_planet_positions(birth_date, birth_time, location):
    """
    Вычисляет позиции планет с использованием библиотеки pyswisseph.
    """
    # Конфигурация
    swe.set_ephe_path('.')  # Укажите путь к эфемеридам Swiss Ephemeris

    # Преобразуем дату и время
    birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")
    julian_day = swe.julday(
        birth_datetime.year, birth_datetime.month, birth_datetime.day,
        birth_datetime.hour + birth_datetime.minute / 60 + birth_datetime.second / 3600
    )

    planets = [
        (swe.SUN, "☉"),
        (swe.MOON, "☽"),
        (swe.MARS, "♂"),
        (swe.VENUS, "♀"),
        (swe.MERCURY, "☿"),
        (swe.JUPITER, "♃"),
        (swe.SATURN, "♄")
    ]

    positions = []
    for planet, symbol in planets:
        position, _ = swe.calc_ut(julian_day, planet)
        positions.append((symbol, position[0]))  # position[0] — долгота планеты

    return positions


async def draw_south_indian_chart(planets):
    """
    Генерирует South Indian Chart на основе позиций планет.
    Возвращает изображение в формате BytesIO.
    """
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

    # Сохраняем изображение в BytesIO
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf
