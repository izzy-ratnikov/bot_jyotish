import io
import matplotlib.pyplot as plt
from datetime import datetime
import asyncio

def calculate_planet_positions(birth_date, birth_time, location):
    """
    Заглушка для вычисления позиций планет на основе даты, времени и местоположения.
    Вместо этого используйте библиотеку астрологии, например, `pyswisseph`.
    """
    # Пример возвращаемых данных: имя планеты и примерная долгота
    return [
        ('☉', 5),    # Солнце
        ('☽', 45),   # Луна
        ('♂', 80),   # Марс
        ('♀', 115),  # Венера
        ('☿', 155),  # Меркурий
        ('♃', 200),  # Юпитер
        ('♄', 270),  # Сатурн
    ]


def draw_south_indian_chart(planets):
    """
    Генерирует South Indian Chart на основе позиций планет.
    Возвращает изображение в формате BytesIO.
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # Рисуем карту
    outer_size = 4
    mid = outer_size / 2

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

    # Добавляем планеты
    for planet, position in planets:
        house = ((int(position / 30) + 1) % 12) or 12
        x = mid if house % 2 == 1 else outer_size - mid
        y = mid if house % 2 == 0 else outer_size - mid
        ax.text(x, y, planet, fontsize=12, ha='center', va='center')

    plt.axis('equal')
    plt.axis('off')

    # Сохраняем изображение в BytesIO
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf


async def build_astrological_chart(birth_date, birth_time, location):
    """
    Выполняет полный цикл расчёта и генерации карты.
    """
    # Преобразуем дату и время в объект datetime
    birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M:%S")

    # Вычисляем координаты и позиции планет
    planets = calculate_planet_positions(birth_date, birth_time, location)

    # Генерируем South Indian Chart
    chart_image = draw_south_indian_chart(planets)

    return location, chart_image

