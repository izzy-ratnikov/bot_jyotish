import matplotlib.pyplot as plt
import swisseph as swe
import io

from src.utils.chart_data import planet_positions_by_house, zodiac_signs_list, zodiac_coords, polygons, planets, \
    zodiac_names, get_basic_astro_data, add_position_data, position_data_with_retrograde


async def calculate_planet_positions(birth_date, birth_time, location):
    astro_data = await get_basic_astro_data(birth_date, birth_time, location)
    julian_day = astro_data["julian_day"]

    zodiac_signs = {}
    positions = []

    rahu_position = None
    ketu_position = None

    for planet, symbol in planets:
        position, flags = swe.calc_ut(julian_day, planet, swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED)
        longitude = position[0]
        speed = position[3]

        is_retrograde = speed < 0

        if symbol == "Ra":
            rahu_position = longitude
            continue
        elif symbol == "Ke":
            ketu_position = longitude
            continue

        position_data_with_retrograde(symbol, longitude, positions, zodiac_signs, is_retrograde)

    if rahu_position is not None and ketu_position is not None:
        ketu_position = (rahu_position + 180) % 360

        position_data_with_retrograde("Ra", rahu_position, positions, zodiac_signs, True)
        position_data_with_retrograde("Ke", ketu_position, positions, zodiac_signs, True)
    return positions, zodiac_signs


async def calculate_asc(birth_date, birth_time, location):
    astro_data = await get_basic_astro_data(birth_date, birth_time, location)
    julian_day = astro_data["julian_day"]
    latitude = astro_data["latitude"]
    longitude = astro_data["longitude"]

    zodiac_signs = {}
    positions = []

    house_positions = swe.houses(julian_day, latitude, longitude, b'P')
    asc_position = house_positions[0][0] - 23.88
    asc_position = asc_position % 360

    add_position_data("Asc", asc_position, positions, zodiac_signs)

    return positions, zodiac_signs


async def draw_north_indian_chart(ascendant_sign, planet_positions):
    fig, ax = plt.subplots(figsize=(9, 9))
    outer_size = 410

    square = plt.Rectangle((5, 5), 410, 410, edgecolor='black', facecolor='black', linewidth=3)
    ax.add_patch(square)

    for points in polygons.values():
        polygon = plt.Polygon(points, edgecolor='black', facecolor='white')
        ax.add_patch(polygon)

    ascendant_index = zodiac_signs_list.index(ascendant_sign)
    house_planet_count = [0] * 12
    house_aspect_count = [0] * 12
    vertical_spacing = 20
    base_x_offset = 10
    base_y_offset = 10

    for i in range(12):
        sign_index = (ascendant_index + i) % 12
        sign = zodiac_signs_list[sign_index]
        x = zodiac_coords[i]["x"] + 15
        y = zodiac_coords[i]["y"] - 7
        ax.text(x, y, sign, fontsize=12, ha='center', va='center', color='black')

    def is_point_in_polygon(x, y, polygon_points):
        """Проверка, находится ли точка внутри полигона"""
        from matplotlib.path import Path
        return Path(polygon_points).contains_point((x, y))

    def calculate_aspects(planet, house_index):
        aspects = []
        if planet.startswith("Su"):
            aspects.append((house_index + 6) % 12)
        elif planet.startswith("Mo"):
            aspects.append((house_index + 6) % 12)
        elif planet.startswith("Ve"):
            aspects.append((house_index + 6) % 12)
        elif planet.startswith("Me"):
            aspects.append((house_index + 6) % 12)
        elif planet.startswith("Jp"):
            aspects.extend([(house_index + 4) % 12, (house_index + 6) % 12, (house_index + 8) % 12])
        elif planet.startswith("Sa"):
            aspects.extend([(house_index + 2) % 12, (house_index + 6) % 12, (house_index + 9) % 12])
        elif planet.startswith("Ma"):
            aspects.extend([(house_index + 3) % 12, (house_index + 6) % 12, (house_index + 7) % 12])
        elif planet.startswith("(Ra)"):
            aspects.extend([(house_index + 4) % 12, (house_index + 6) % 12, (house_index + 8) % 12])
        return aspects

    occupied_positions = {i: [] for i in range(12)}

    for planet, position in planet_positions:
        house_index = int(position // 30)
        house_index = (house_index - ascendant_index) % 12
        coords = planet_positions_by_house[house_index]
        planet_index = house_planet_count[house_index]
        house_planet_count[house_index] += 1

        polygon_points = polygons[list(polygons.keys())[house_index]]

        if planet_index < len(coords):
            x = coords[planet_index]["x"] + base_x_offset
            y = outer_size - coords[planet_index]["y"] + base_y_offset
        else:
            x = zodiac_coords[house_index]["x"] + base_x_offset
            y = zodiac_coords[house_index]["y"] - (planet_index - len(coords)) * vertical_spacing + base_y_offset

        while not is_point_in_polygon(x, outer_size - y, polygon_points) or any(
                abs(pos[0] - x) < 20 and abs(pos[1] - y) < 20 for pos in occupied_positions[house_index]
        ):
            x += 5 if x < 200 else -5
            y += 5 if y < 200 else -5
            if x < 10 or x > 400 or y < 10 or y > 400:
                x = min(max(x, 10), 400)
                y = min(max(y, 10), 400)
                break

        occupied_positions[house_index].append((x, y))
        ax.text(x, y, planet, fontsize=14, ha='center', va='center', color='black', fontweight='bold')

    for planet, position in planet_positions:
        house_index = int(position // 30)
        house_index = (house_index - ascendant_index) % 12
        aspects = calculate_aspects(planet, house_index)

        for aspect_house_index in aspects:
            coords = planet_positions_by_house[aspect_house_index]
            aspect_index = house_aspect_count[aspect_house_index]
            house_aspect_count[aspect_house_index] += 1
            polygon_points = polygons[list(polygons.keys())[aspect_house_index]]

            if aspect_index < len(coords):
                x = coords[aspect_index]["x"] + base_x_offset - 15
                y = outer_size - coords[aspect_index]["y"] + base_y_offset - 5
            else:
                x = zodiac_coords[aspect_house_index]["x"] + base_x_offset - 15
                y = zodiac_coords[aspect_house_index]["y"] - (
                        aspect_index - len(coords)) * vertical_spacing + base_y_offset - 5

            while not is_point_in_polygon(x, outer_size - y, polygon_points) or any(
                    abs(pos[0] - x) < 20 and abs(pos[1] - y) < 20 for pos in occupied_positions[aspect_house_index]
            ):
                x += 5 if x < 200 else -5
                y += 5 if y < 200 else -5
                if x < 10 or x > 400 or y < 10 or y > 400:
                    x = min(max(x, 10), 400)
                    y = min(max(y, 10), 400)
                    break

            occupied_positions[aspect_house_index].append((x, y))
            aspect_planet = planet.replace("↑", "").replace("↓", "").replace("\u035F", "").replace("(", "").replace(")",
                                                                                                                    "")
            ax.text(x, y, aspect_planet, fontsize=11, ha='center', va='center', color='gray', alpha=0.5,
                    fontweight='bold')

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
