import matplotlib.pyplot as plt
import swisseph as swe
import io

from openai import OpenAI

from src.dispatcher.dispatcher import openai_api_key
from src.utils.chart_data import planet_positions_by_house, zodiac_signs_list, zodiac_coords, polygons, planets, \
    zodiac_names, get_basic_astro_data, add_position_data


async def calculate_planet_positions(birth_date, birth_time, location):
    astro_data = await get_basic_astro_data(birth_date, birth_time, location)
    julian_day = astro_data["julian_day"]

    zodiac_signs = {}
    positions = []

    rahu_position = None
    ketu_position = None

    for planet, symbol in planets:
        position, _ = swe.calc_ut(julian_day, planet, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        longitude = position[0]

        if symbol == "Ra":
            rahu_position = longitude
            continue
        elif symbol == "Ke":
            ketu_position = longitude
            continue

        add_position_data(symbol, longitude, positions, zodiac_signs)

    if rahu_position is not None and ketu_position is not None:
        ketu_position = (rahu_position + 180) % 360

        add_position_data("Ra", rahu_position, positions, zodiac_signs)
        add_position_data("Ke", ketu_position, positions, zodiac_signs)

    return positions, zodiac_signs


async def calculate_asc(birth_date, birth_time, location):
    astro_data = await get_basic_astro_data(birth_date, birth_time, location)
    julian_day = astro_data["julian_day"]
    latitude = astro_data["latitude"]
    longitude = astro_data["longitude"]

    zodiac_signs = {}
    positions = []

    house_positions = swe.houses(julian_day, latitude, longitude, b'P')
    asc_position = house_positions[0][0] - 23.8
    asc_position = asc_position % 360

    add_position_data("Asc", asc_position, positions, zodiac_signs)

    return positions, zodiac_signs


async def draw_north_indian_chart(ascendant_sign, planet_positions):
    fig, ax = plt.subplots(figsize=(8, 8))

    outer_size = 410

    square = plt.Rectangle((5, 5), 410, 410, edgecolor='black', facecolor='black', linewidth=3)
    ax.add_patch(square)

    for points in polygons.values():
        polygon = plt.Polygon(points, edgecolor='black', facecolor='white')
        ax.add_patch(polygon)

    ascendant_index = zodiac_signs_list.index(ascendant_sign)

    house_planet_count = [0] * 12
    vertical_spacing = 20
    x_offset = 10

    for i in range(12):
        sign_index = (ascendant_index + i) % 12
        sign = zodiac_signs_list[sign_index]
        x = zodiac_coords[i]["x"] + 15
        y = zodiac_coords[i]["y"] - 7
        ax.text(x, y, sign, fontsize=18, ha='center', va='center', color='black')

    for planet, position in planet_positions:

        house_index = int(position // 30)
        house_index = (house_index - ascendant_index) % 12

        coords = planet_positions_by_house[house_index]

        planet_index = house_planet_count[house_index]
        house_planet_count[house_index] += 1

        if planet_index < len(coords):
            x = coords[planet_index]["x"] + x_offset
            y = outer_size - coords[planet_index]["y"]
        else:

            x = zodiac_coords[house_index]["x"] + 15 + x_offset
            y = zodiac_coords[house_index]["y"] - 7 - (planet_index - len(coords)) * vertical_spacing

        ax.text(x, y, planet, fontsize=18, ha='center', va='center', color='black', fontweight='bold')

    ax.set_xlim(0, outer_size + 10)
    ax.set_ylim(0, outer_size + 10)
    ax.set_aspect('equal')
    ax.axis('off')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    buf.seek(0)

    return buf


async def get_house_info(ascendant_sign, planet_positions):
    ascendant_index = zodiac_names.index(ascendant_sign)

    house_info = []

    for i in range(12):

        sign_index = (ascendant_index + i) % 12
        sign = zodiac_names[sign_index]

        planets_in_house = []

        for planet, position in planet_positions:
            house_index = int(position // 30)
            house_index = (house_index - ascendant_index) % 12
            if house_index == i:
                planets_in_house.append(planet)

        house_str = f"{i + 1}-й\t{sign}\t{', '.join(planets_in_house)}"
        house_info.append(house_str)

    return house_info


async def chat_gpt(house_info):
    client = OpenAI(api_key=openai_api_key)

    prompt = f"""
    Ты астролог высокого уровня джйотиш, который отвечает на вопросы максимально подробно и максимально корректно.
    Расшифруй натальную карту на основе следующих данных:
    {house_info}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "assistant", "content": prompt}],
        stream=False,
    )
    return response.choices[0].message.content
