from datetime import datetime
from timezonefinder import TimezoneFinder
from pytz import timezone, utc
from geopy.geocoders import Nominatim
import swisseph as swe


async def get_basic_astro_data(birth_date, birth_time, location):
    swe.set_ephe_path('.')
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    geolocator = Nominatim(user_agent="astro_bot")
    loc = geolocator.geocode(location)
    if not loc:
        raise ValueError(f"Локация '{location}' не найдена.")
    latitude, longitude = loc.latitude, loc.longitude

    print(
        f"Координаты для '{location}': Широта: {latitude}, "
        f"Долгота: {longitude}"
    )

    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=latitude, lng=longitude)
    if not tz_name:
        raise ValueError(
            f"Не удалось определить часовой пояс для локации '{location}'."
        )
    local_tz = timezone(tz_name)

    birth_datetime = datetime.strptime(
        f"{birth_date} {birth_time}", "%d-%m-%Y %H:%M:%S"
    )
    local_datetime = local_tz.localize(birth_datetime)
    utc_datetime = local_datetime.astimezone(utc)

    julian_day = swe.julday(
        utc_datetime.year,
        utc_datetime.month,
        utc_datetime.day,
        (
            utc_datetime.hour +
            utc_datetime.minute / 60 +
            utc_datetime.second / 3600
        )
    )

    elevation = 0
    swe.set_topo(longitude, latitude, elevation)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "julian_day": julian_day,
        "utc_datetime": utc_datetime
    }


def calculate_zodiac_position(longitude):
    zodiac_index = int(longitude // 30)
    zodiac_sign = zodiac_names[zodiac_index]
    degree = int(longitude % 30)
    minutes = int((longitude % 1) * 60)
    seconds = int(((longitude % 1) * 60 % 1) * 60)
    return zodiac_sign, degree, minutes, seconds


def clean_planet_symbol(symbol):
    """
    Очищает символ планеты от обозначений экзальтации, дебилитации,
    ретроградности и мулатриконы.
    """
    for char in ["↑", "↓", "\u035F", "(", ")"]:
        symbol = symbol.replace(char, "")
    return symbol.strip()


NAKSHATRAS = {
    "Овен": [
        (
            "Ашвини",
            0.0, 13.3333,
            [
                (0.0, 3.3333),
                (3.3333, 6.6667),
                (6.6667, 10.0),
                (10.0, 13.3333),
            ],
        ),
        (
            "Бхарани",
            13.3333, 26.6667,
            [
                (13.3333, 16.6667),
                (16.6667, 20.0),
                (20.0, 23.3333),
                (23.3333, 26.6667),
            ],
        ),
        (
            "Криттика",
            26.6667,
            30.0,
            [(26.6667, 30.0)],
        ),
    ],
    "Телец": [
        (
            "Криттика",
            0.0,
            10.0,
            [
                (0.0, 3.3333),
                (3.3333, 6.6667),
                (6.6667, 10.0),
            ]
        ),
        (
            "Рохини",
            10.0,
            23.3333,
            [
                (10.0, 13.3333),
                (13.3333, 16.6667),
                (16.6667, 20.0),
                (20.0, 23.3333),
            ],
        ),
        (
            "Мригашира",
            23.3333,
            30.0,
            [
                (23.3333, 26.6667),
                (26.6667, 30.0),
            ],
        ),
    ],
    "Близнецы": [
        (
            "Мригашира",
            0.0,
            6.6667,
            [
                (0.0, 3.3333),
                (3.3333, 6.6667),
            ],
        ),
        (
            "Ардра",
            6.6667,
            20.0,
            [
                (6.6667, 10.0),
                (10.0, 13.3333),
                (13.3333, 16.6667),
                (16.6667, 20.0),
            ],
        ),
        (
            "Пунарвасу",
            20.0,
            30.0,
            [
                (20.0, 23.3333),
                (23.3333, 26.6667),
                (26.6667, 30.0),
            ],
        ),
    ],
    "Рак": [
        (
            "Пунарвасу",
            0.0,
            3.3333,
            [(0.0, 3.3333)]
        ),
        (
            "Пушья",
            3.3333,
            16.6667,
            [
                (3.3333, 6.6667),
                (6.6667, 10.0),
                (10.0, 13.3333),
                (13.3333, 16.6667),
            ],
        ),
        (
            "Ашлеша",
            16.6667,
            30.0,
            [
                (16.6667, 20.0),
                (20.0, 23.3333),
                (23.3333, 26.6667),
                (26.6667, 30.0),
            ],
        ),
    ],
    "Лев": [
        (
            "Магха",
            0.0,
            13.3333,
            [
                (0.0, 3.3333),
                (3.3333, 6.6667),
                (6.6667, 10.0),
                (10.0, 13.3333),
            ],
        ),
        (
            "Пурва-Пхалгуни",
            13.3333,
            26.6667,
            [
                (13.3333, 16.6667),
                (16.6667, 20.0),
                (20.0, 23.3333),
                (23.3333, 26.6667),
            ],
        ),
        (
            "Уттара-Пхалгуни",
            26.6667,
            30.0,
            [(26.6667, 30.0)],
        ),
    ],
    "Дева": [
        (
            "Уттара-Пхалгуни",
            0.0,
            10.0,
            [
                (0.0, 3.3333),
                (3.3333, 6.6667),
                (6.6667, 10.0),
            ],
        ),
        (
            "Хаста",
            10.0,
            23.3333,
            [
                (10.0, 13.3333),
                (13.3333, 16.6667),
                (16.6667, 20.0),
                (20.0, 23.3333),
            ],
        ),
        (
            "Читра",
            23.3333,
            30.0,
            [(23.3333, 26.6667), (26.6667, 30.0)],
        ),
    ],
    "Весы": [
        (
            "Читра",
            0.0,
            6.6667,
            [(0.0, 3.3333), (3.3333, 6.6667)],
        ),
        (
            "Свати",
            6.6667,
            20.0,
            [
                (6.6667, 10.0),
                (10.0, 13.3333),
                (13.3333, 16.6667),
                (16.6667, 20.0),
            ],
        ),
        (
            "Вишакха",
            20.0,
            30.0,
            [(20.0, 23.3333), (23.3333, 26.6667), (26.6667, 30.0)],
        ),
    ],
    "Скорпион": [
        (
            "Вишакха",
            0.0,
            3.3333,
            [(0.0, 3.3333)],
        ),
        (
            "Анурадха",
            3.3333,
            16.6667,
            [
                (3.3333, 6.6667),
                (6.6667, 10.0),
                (10.0, 13.3333),
                (13.3333, 16.6667),
            ],
        ),
        (
            "Джиештха",
            16.6667,
            30.0,
            [
                (16.6667, 20.0),
                (20.0, 23.3333),
                (23.3333, 26.6667),
                (26.6667, 30.0),
            ],
        ),
    ],
    "Стрелец": [
        (
            "Мула",
            0.0,
            13.3333,
            [
                (0.0, 3.3333),
                (3.3333, 6.6667),
                (6.6667, 10.0),
                (10.0, 13.3333),
            ],
        ),
        (
            "Пурва-Ашадха",
            13.3333,
            26.6667,
            [
                (13.3333, 16.6667),
                (16.6667, 20.0),
                (20.0, 23.3333),
                (23.3333, 26.6667),
            ],
        ),
        (
            "Уттара-Ашадха",
            26.6667,
            30.0,
            [(26.6667, 30.0)],
        ),
    ],
    "Козерог": [
        (
            "Уттара-Ашадха",
            0.0,
            10.0,
            [(0.0, 3.3333), (3.3333, 6.6667), (6.6667, 10.0)],
        ),
        (
            "Шравана",
            10.0,
            23.3333,
            [
                (10.0, 13.3333),
                (13.3333, 16.6667),
                (16.6667, 20.0),
                (20.0, 23.3333),
            ],
        ),
        (
            "Дхаништха",
            23.3333,
            30.0,
            [(23.3333, 26.6667), (26.6667, 30.0)],
        ),
    ],
    "Водолей": [
        (
            "Дхаништха",
            0.0,
            6.6667,
            [(0.0, 3.3333), (3.3333, 6.6667)],
        ),
        (
            "Шатабхиша",
            6.6667,
            20.0,
            [
                (6.6667, 10.0),
                (10.0, 13.3333),
                (13.3333, 16.6667),
                (16.6667, 20.0),
            ],
        ),
        (
            "Пурва-Бхадрапада",
            20.0,
            30.0,
            [(20.0, 23.3333), (23.3333, 26.6667), (26.6667, 30.0)],
        ),
    ],
    "Рыбы": [
        (
            "Пурва-Бхадрапада",
            0.0,
            3.3333,
            [(0.0, 3.3333)],
        ),
        (
            "Уттара-Бхадрапада",
            3.3333,
            16.6667,
            [
                (3.3333, 6.6667),
                (6.6667, 10.0),
                (10.0, 13.3333),
                (13.3333, 16.6667),
            ],
        ),
        (
            "Ревати",
            16.6667,
            30.0,
            [
                (16.6667, 20.0),
                (20.0, 23.3333),
                (23.3333, 26.6667),
                (26.6667, 30.0),
            ],
        ),
    ]
}


def to_decimal_degrees(degrees, minutes, seconds):
    return degrees + minutes / 60 + seconds / 3600


def add_position_data(symbol, longitude, positions, zodiac_signs):
    zodiac_sign, degree, minutes, seconds = calculate_zodiac_position(
        longitude
    )
    positions.append((symbol, longitude))
    zodiac_signs[symbol] = (zodiac_sign, degree, minutes, seconds)


def position_data_with_retrograde(
        symbol,
        longitude,
        positions,
        zodiac_signs,
        is_retrograde=False
):
    zodiac_sign, degree, minutes, seconds = calculate_zodiac_position(
        longitude
    )

    zodiac_name = zodiac_symbol_to_name.get(zodiac_sign, "")
    is_mula_trikona = zodiac_name == mula_trikona_signs.get(symbol, "")

    is_exaltation = zodiac_name == exaltation_signs.get(symbol, "")
    is_debilitation = zodiac_name == debilitation_signs.get(symbol, "")
    display_symbol = symbol

    if is_retrograde:
        display_symbol = f"({display_symbol})"

    if is_exaltation:
        display_symbol = f"{display_symbol}↑"
    elif is_debilitation:
        display_symbol = f"{display_symbol}↓"

    if is_mula_trikona:
        display_symbol = f"{display_symbol[0]}\u035F{display_symbol[1:]}"

    positions.append((display_symbol, longitude))
    zodiac_signs[symbol] = (zodiac_sign, degree, minutes, seconds)


mula_trikona_signs = {
    "Su": "Leo",
    "Ma": "Aries",
    "Jp": "Sagittarius",
    "Ve": "Libra",
    "Sa": "Aquarius",
}

zodiac_symbol_to_name = {
    "♈": "Aries",
    "♉": "Taurus",
    "♊": "Gemini",
    "♋": "Cancer",
    "♌": "Leo",
    "♍": "Virgo",
    "♎": "Libra",
    "♏": "Scorpio",
    "♐": "Sagittarius",
    "♑": "Capricorn",
    "♒": "Aquarius",
    "♓": "Pisces",
}
zodiac_to_number = {
    "♈": "1",
    "♉": "2",
    "♊": "3",
    "♋": "4",
    "♌": "5",
    "♍": "6",
    "♎": "7",
    "♏": "8",
    "♐": "9",
    "♑": "10",
    "♒": "11",
    "♓": "12"
}

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

zodiac_signs_list = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
]

planet_positions_by_house = [
    # Tan Bhav Planets positions
    [
        {"y": 120, "x": 195}, {"y": 80, "x": 205}, {"y": 118, "x": 235},
        {"y": 80, "x": 245}, {"y": 40, "x": 215}, {"y": 65, "x": 175},
        {"y": 110, "x": 155}, {"y": 102, "x": 273}
    ],
    # Dhan Bhav Planets positions
    [
        {"x": 105, "y": 41}, {"y": 20, "x": 140}, {"y": 19, "x": 80},
        {"y": 55, "x": 133}, {"y": 55, "x": 83}, {"y": 21, "x": 50},
        {"y": 21, "x": 170}, {"y": 24, "x": 115}
    ],
    # Anuj Bhav Planets positions
    [
        {"x": 50, "y": 105}, {"x": 25, "y": 140}, {"x": 22, "y": 80},
        {"x": 55, "y": 130}, {"x": 60, "y": 85}, {"x": 23, "y": 50},
        {"x": 23, "y": 170}, {"x": 26, "y": 115}
    ],
    # Maata Bhav Planets positions
    [
        {"x": 130, "y": 195}, {"x": 90, "y": 205}, {"x": 128, "y": 225},
        {"x": 90, "y": 235}, {"x": 50, "y": 205}, {"x": 75, "y": 175},
        {"x": 120, "y": 155}, {"x": 112, "y": 273}
    ],
    # Santan Bhav Planets positions
    [
        {"x": 50, "y": 305}, {"x": 25, "y": 340}, {"x": 22, "y": 280},
        {"x": 55, "y": 333}, {"x": 55, "y": 283}, {"x": 23, "y": 250},
        {"x": 23, "y": 370}, {"x": 26, "y": 315}
    ],
    # Rog Bhav Planets positions
    [
        {"x": 107, "y": 355}, {"x": 70, "y": 370}, {"x": 138, "y": 393},
        {"x": 110, "y": 380}, {"x": 90, "y": 398}, {"x": 50, "y": 395},
        {"x": 170, "y": 397}, {"x": 137, "y": 365}
    ],
    # Dampathya Bhav Planets positions
    [
        {"y": 260, "x": 187}, {"y": 310, "x": 205}, {"y": 290, "x": 230},
        {"y": 310, "x": 240}, {"y": 360, "x": 215}, {"y": 335, "x": 175},
        {"y": 300, "x": 160}, {"y": 310, "x": 270}
    ],
    # Aayu Bhav Planets positions
    [
        {"x": 310, "y": 360}, {"x": 270, "y": 375}, {"x": 338, "y": 398},
        {"x": 310, "y": 385}, {"x": 290, "y": 403}, {"x": 250, "y": 400},
        {"x": 372, "y": 402}, {"x": 340, "y": 370}
    ],
    # Bhagya Bhav Planets positions
    [
        {"x": 370, "y": 315}, {"x": 360, "y": 345}, {"x": 360, "y": 290},
        {"x": 390, "y": 278}, {"x": 390, "y": 340}, {"x": 379, "y": 365},
        {"x": 393, "y": 255}, {"x": 395, "y": 387}
    ],
    # Karma Bhav Planets positions
    [
        {"x": 280, "y": 205}, {"x": 330, "y": 210}, {"x": 292, "y": 240},
        {"x": 330, "y": 250}, {"x": 370, "y": 220}, {"x": 345, "y": 185},
        {"x": 300, "y": 165}, {"x": 308, "y": 283}
    ],
    # Laab Bhav Planets positions
    [
        {"x": 370, "y": 115}, {"x": 360, "y": 145}, {"x": 360, "y": 90},
        {"x": 390, "y": 78}, {"x": 390, "y": 140}, {"x": 379, "y": 165},
        {"x": 393, "y": 55}, {"x": 395, "y": 187}
    ],
    # Karch Bhav Planets positions
    [
        {"x": 306, "y": 61}, {"y": 40, "x": 340}, {"y": 37, "x": 280},
        {"y": 75, "x": 333}, {"y": 75, "x": 283}, {"y": 36, "x": 250},
        {"y": 36, "x": 370}, {"y": 41, "x": 315}
    ]
]

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

zodiac_names = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

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

exaltation_signs = {
    "Su": "Aries",
    "Mo": "Taurus",
    "Ma": "Capricorn",
    "Me": "Virgo",
    "Jp": "Cancer",
    "Ve": "Pisces",
    "Sa": "Libra",
    "Ra": "Taurus",
    "Ke": "Scorpio"
}
debilitation_signs = {
    "Su": "Libra",
    "Mo": "Scorpio",
    "Ma": "Cancer",
    "Me": "Pisces",
    "Jp": "Capricorn",
    "Ve": "Virgo",
    "Sa": "Aries",
    "Ra": "Scorpio",
    "Ke": "Taurus"
}

zodiac_symbols_to_names = {
    "♈": "Овен", "♉": "Телец", "♊": "Близнецы", "♋": "Рак",
    "♌": "Лев", "♍": "Дева", "♎": "Весы", "♏": "Скорпион",
    "♐": "Стрелец", "♑": "Козерог", "♒": "Водолей", "♓": "Рыбы"
}

nakshatra_planets = {
    "Ашвини": "Кету",
    "Бхарани": "Венера",
    "Криттика": "Солнце",
    "Рохини": "Луна",
    "Мригашира": "Марс",
    "Ардра": "Раху",
    "Пунарвасу": "Юпитер",
    "Пушья": "Сатурн",
    "Ашлеша": "Меркурий",
    "Магха": "Кету",
    "Пурва-пхалгуни": "Венера",
    "Уттара-пхалгуни": "Солнце",
    "Хаста": "Луна",
    "Читра": "Марс",
    "Свати": "Раху",
    "Вишакха": "Юпитер",
    "Анурадха": "Сатурн",
    "Джиештха": "Меркурий",
    "Мула": "Кету",
    "Пурва-ашадха": "Венера",
    "Уттара-ашадха": "Солнце",
    "Шравана": "Луна",
    "Дхаништха": "Марс",
    "Шатабхиша": "Раху",
    "Пурва-бхадрапада": "Юпитер",
    "Уттара-бхадрапада": "Сатурн",
    "Ревати": "Меркурий"
}


def get_starting_planet(moon_nakshatra):
    return nakshatra_planets.get(moon_nakshatra, "Неизвестно")


planet_periods = {
    "Кету": 7,
    "Венера": 20,
    "Солнце": 6,
    "Луна": 10,
    "Марс": 7,
    "Раху": 18,
    "Юпитер": 16,
    "Сатурн": 19,
    "Меркурий": 17
}

dasha_order = [
    "Кету",
    "Венера",
    "Солнце",
    "Луна",
    "Марс",
    "Раху",
    "Юпитер",
    "Сатурн",
    "Меркурий",
]


def calculate_remaining_time(
        moon_degree,
        starting_planet,
        nakshatra_length=13.3333,
):
    period_length = planet_periods[starting_planet]
    percent_passed = (moon_degree / nakshatra_length) * 100
    years_passed = period_length * (percent_passed / 100)
    years_remaining = period_length - years_passed
    return years_remaining, years_passed
