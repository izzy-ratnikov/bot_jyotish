from typing import Tuple
from io import BytesIO


async def build_astrological_chart(birth_date: str, birth_time: str, location: str) -> Tuple[str, BytesIO]:
    # Логика вычисления координат и построения графика
    coordinates = f"Координаты: {location}"

    chart_image = BytesIO()
    chart_image.write(b"image content")  # Пример изображения
    chart_image.seek(0)

    return coordinates, chart_image
