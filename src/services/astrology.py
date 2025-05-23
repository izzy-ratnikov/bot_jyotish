import matplotlib.pyplot as plt
import swisseph as swe
import io
from matplotlib.path import Path
from src.utils.chart_data import planet_positions_by_house, zodiac_signs_list, zodiac_coords, polygons, planets, \
    zodiac_names, get_basic_astro_data, add_position_data, position_data_with_retrograde, clean_planet_symbol, \
    NAKSHATRAS, planet_periods, dasha_order
from datetime import timedelta
from itertools import accumulate


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


async def calculate_karakas(planets_positions):
    excluded_planets = ["Ra", "Ke"]

    planets_dict = {
        clean_planet_symbol(symbol): longitude
        for symbol, longitude in planets_positions
    }

    filtered_planets = {k: v for k, v in planets_dict.items() if k not in excluded_planets}

    def get_in_sign_longitude(longitude):
        return longitude % 30

    sorted_planets = sorted(
        filtered_planets.items(),
        key=lambda item: get_in_sign_longitude(item[1]),
        reverse=True
    )

    karakas = {
        "(AK)": sorted_planets[0][0],
        "(AмK)": sorted_planets[1][0],
        "(БK)": sorted_planets[2][0],
        "(MK)": sorted_planets[3][0],
        "(ПK)": sorted_planets[4][0],
        "(ГK)": sorted_planets[5][0],
        "(ДK)": sorted_planets[6][0],
    }

    return karakas


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
    planet_house_info = []

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

        max_iterations = 200
        iteration = 0

        while not is_point_in_polygon(x, outer_size - y, polygon_points) or any(
                abs(pos[0] - x) < 20 and abs(pos[1] - y) < 20 for pos in occupied_positions[house_index]
        ):
            x += 5 if x < 200 else -5
            y += 5 if y < 200 else -5
            if x < 10 or x > 400 or y < 10 or y > 400:
                x = min(max(x, 10), 400)
                y = min(max(y, 10), 400)
                break
            iteration += 1
            if iteration > max_iterations:
                print(f"Warning: Max iterations reached for planet {planet} in house {house_index}")
                break

        occupied_positions[house_index].append((x, y))
        ax.text(x, y, planet, fontsize=14, ha='center', va='center', color='black', fontweight='bold')

        planet_house_info.append(f"{planet}, Дом: {house_index + 1}")

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

            max_iterations = 200
            iteration = 0
            while not is_point_in_polygon(x, outer_size - y, polygon_points) or any(
                    abs(pos[0] - x) < 20 and abs(pos[1] - y) < 20 for pos in occupied_positions[aspect_house_index]
            ):
                x += 5 if x < 200 else -5
                y += 5 if y < 200 else -5
                if x < 10 or x > 400 or y < 10 or y > 400:
                    x = min(max(x, 10), 400)
                    y = min(max(y, 10), 400)
                    break
                iteration += 1
                if iteration > max_iterations:
                    print(f"Warning: Max iterations reached for aspect of {planet} in house {aspect_house_index}")
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
    return buf, planet_house_info


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
                cleaned_planet = clean_planet_symbol(planet)
                planets_in_house.append(cleaned_planet)

        house_str = f"{i + 1}-й\t{sign}\t{', '.join(planets_in_house)}"
        house_info.append(house_str)

    return house_info


async def get_nakshatra_and_pada(zodiac_sign, longitude):
    sign_nakshatras = NAKSHATRAS.get(zodiac_sign)
    if not sign_nakshatras:
        return None, None

    in_sign_longitude = longitude % 30
    for nakshatra_name, start, end, pada_ranges in sign_nakshatras:
        if start <= in_sign_longitude < end:
            pada_index = 1
            for pada_start, pada_end in pada_ranges:
                if pada_start <= in_sign_longitude < pada_end:
                    if nakshatra_name == "Читра" and zodiac_sign == "Весы":
                        pada_index += 2
                    elif nakshatra_name == "Мригашира" and zodiac_sign == "Близнецы":
                        pada_index += 2
                    elif nakshatra_name == "Криттика" and zodiac_sign == "Телец":
                        pada_index += 1
                    return nakshatra_name, pada_index
                pada_index += 1
            return nakshatra_name, pada_index - 1
    last_nakshatra = sign_nakshatras[-1]
    return last_nakshatra[0], len(last_nakshatra[3])


async def get_zodiac_sign(longitude):
    zodiac_signs = [
        "Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
        "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"
    ]
    index = int(longitude // 30)
    return zodiac_signs[index]


async def get_moon_degree(planets_positions):
    for planet in planets_positions:
        planet_symbol, longitude = planet
        if "Mo" in planet_symbol:
            nakshatra_number = int(longitude // 13.3333)
            start_of_nakshatra = nakshatra_number * 13.3333
            degree_in_nakshatra = longitude - start_of_nakshatra
            return degree_in_nakshatra
    raise ValueError("Позиция Луны не найдена в данных.")


async def get_moon_nakshatra(planets_positions):
    for planet in planets_positions:
        planet_symbol, longitude = planet
        if "Mo" in planet_symbol:
            zodiac_sign = await get_zodiac_sign(longitude)
            nakshatra, _ = await get_nakshatra_and_pada(zodiac_sign, longitude)
            return nakshatra
    raise ValueError("Позиция Луны не найдена в данных.")


# начало второго и третьего подпериода даши
def years_to_years_months_days(years):
    total_days = years * 365.25
    years_int = int(total_days // 365.25)
    remaining_days = total_days - (years_int * 365.25)
    months = int(remaining_days // 30.4375)
    days = int(remaining_days - (months * 30.4375))
    return years_int, months, days


async def calculate_pratyantardasha(antardasha_planet,
                                    antardasha_actual_start,
                                    antardasha_actual_duration_years,
                                    antardasha_theoretical_start,
                                    antardasha_theoretical_duration_years):
    pratyantardasha_text = f"   Под-подпериоды (Пратьянтардаша) в Антардаше {antardasha_planet}:\n\n"

    antardasha_actual_end = antardasha_actual_start + timedelta(days=antardasha_actual_duration_years * 365.25)

    D_ant_theoretical = antardasha_theoretical_duration_years

    start_index = dasha_order.index(antardasha_planet)
    sequence = dasha_order[start_index:] + dasha_order[:start_index]

    cumulative_theoretical_prat_days = 0.0

    for i, planet in enumerate(sequence):

        prat_theoretical_duration_years = (planet_periods[planet] * D_ant_theoretical) / 120
        prat_theoretical_duration_days = prat_theoretical_duration_years * 365.25
        prat_theoretical_start = antardasha_theoretical_start + timedelta(days=cumulative_theoretical_prat_days)
        prat_theoretical_end = prat_theoretical_start + timedelta(days=prat_theoretical_duration_days)

        display_start = max(prat_theoretical_start, antardasha_actual_start)
        display_end = min(prat_theoretical_end, antardasha_actual_end)

        cumulative_theoretical_prat_days += prat_theoretical_duration_days

        if display_end > display_start:
            actual_duration = display_end - display_start

            if actual_duration.total_seconds() > 3600:
                actual_years = actual_duration.total_seconds() / (365.25 * 24 * 60 * 60)
                years, months, days = years_to_years_months_days(actual_years)

                if years >= 0 and months >= 0 and days >= 0:
                    pratyantardasha_text += (

                        f"     • {planet}: {years} лет, {months} мес., {days} дн.\n"
                        f"       Начало: {display_start.strftime('%d.%m.%Y')}\n"
                        f"       Конец: {display_end.strftime('%d.%m.%Y')}\n"
                    )

        if prat_theoretical_start >= antardasha_actual_end:
            break

    if cumulative_theoretical_prat_days == 0.0 and pratyantardasha_text.endswith(":\n\n"):
        pratyantardasha_text += "       (Нет под-подпериодов в этом отрезке)\n"

    return pratyantardasha_text


async def calculate_antardasha(mahadasha_planet, full_period_years, mahadasha_start, is_first=False, is_last=False,
                               birth_date=None, end_of_life=None):
    antardasha_text = f"\nПодпериоды (Антардаша) в Махадаше {mahadasha_planet}:\n\n"
    D = full_period_years
    start_index = dasha_order.index(mahadasha_planet)
    sequence = dasha_order[start_index:] + dasha_order[:start_index]

    cumulative_theoretical_days = 0.0

    for i, planet in enumerate(sequence):

        theoretical_duration_years = (planet_periods[planet] * D) / 120
        theoretical_duration_days = theoretical_duration_years * 365.25

        theoretical_start_date = mahadasha_start + timedelta(days=cumulative_theoretical_days)
        theoretical_end_date = theoretical_start_date + timedelta(days=theoretical_duration_days)

        start_date = theoretical_start_date
        end_date = theoretical_end_date

        if is_first and birth_date and end_date < birth_date:
            cumulative_theoretical_days += theoretical_duration_days
            continue
        if is_first and birth_date and start_date < birth_date:
            start_date = birth_date

        if is_last and end_of_life and start_date > end_of_life:
            cumulative_theoretical_days += theoretical_duration_days
            break
        if is_last and end_of_life and end_date > end_of_life:
            end_date = end_of_life

        if end_date <= start_date:
            cumulative_theoretical_days += theoretical_duration_days
            continue

        actual_duration = end_date - start_date

        if actual_duration.total_seconds() < 1:
            cumulative_theoretical_days += theoretical_duration_days
            continue

        actual_years = actual_duration.days / 365.25

        if actual_years > 1e-9:
            years, months, days = years_to_years_months_days(actual_years)
            antardasha_text += (
                f"▸ {planet}: {years} лет, {months} мес., {days} дн.\n"
                f"  Начало: {start_date.strftime('%d.%m.%Y')}\n"
                f"  Конец: {end_date.strftime('%d.%m.%Y')}\n"
            )
            pratyantardasha_text = await calculate_pratyantardasha(
                antardasha_planet=planet,
                antardasha_actual_start=start_date,
                antardasha_actual_duration_years=actual_years,
                antardasha_theoretical_start=theoretical_start_date,
                antardasha_theoretical_duration_years=theoretical_duration_years

            )
            antardasha_text += pratyantardasha_text + "\n"

        cumulative_theoretical_days += theoretical_duration_days

        if is_last and end_of_life and end_date >= end_of_life:
            break

    return antardasha_text
