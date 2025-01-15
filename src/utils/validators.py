from datetime import datetime
import re


def validate_date(date: str) -> bool:
    try:
        datetime.strptime(date, "%d-%m-%Y")
        return True
    except ValueError:
        return False


def validate_time(time: str) -> bool:
    try:
        datetime.strptime(time, "%H:%M:%S")
        return True
    except ValueError:
        return False


def validate_location(location: str) -> bool:
    return bool(re.match(r"^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?((1[0-7]\d)|([1-9]?\d))(\.\d+)?$", location))
