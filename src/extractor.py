import re
from datetime import date
from typing import Optional


MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}

EXPLICIT_ZONE_PATTERN = re.compile(
    r"\bзона\s*:\s*([а-яёa-z-]+)",
    re.IGNORECASE,
)

CHILD_ID_PATTERN = re.compile(
    r"\bCH[-\s]?(\d{4})\b",
    re.IGNORECASE,
)

NUMERIC_DATE_PATTERN = re.compile(
    r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})\b"
)

TEXT_DATE_PATTERN = re.compile(
    r"\b(\d{1,2})\s+"
    r"(января|февраля|марта|апреля|мая|июня|июля|августа|"
    r"сентября|октября|ноября|декабря)"
    r"(?:\s+(\d{4}))?\s*г?\.?",
    re.IGNORECASE,
)

SLEEP_HOURS_MINUTES_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*ч(?:ас(?:а|ов)?)?"
    r"(?:\s*(\d+)\s*мин(?:ут)?)?",
    re.IGNORECASE,
)

SLEEP_DECIMAL_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*час(?:а|ов)?",
    re.IGNORECASE,
)

SLEEP_COLON_PATTERN = re.compile(
    r"\b(\d{1,2}):(\d{2})\b"
)

SLEEP_MINUTES_PATTERN = re.compile(
    r"(\d+)\s*мин(?:ут)?",
    re.IGNORECASE,
)

SLEEP_CONTEXT_PATTERN = re.compile(
    r"\b(сон|сна|спал|спала|спали|заснул|заснула|засыпал|"
    r"ночью|ночной)\b",
    re.IGNORECASE,
)

AUTHOR_PATTERNS = [
    re.compile(
        r"\b(?:тьютор|тьют\.?)\s*"
        r"([А-ЯЁA-Z][а-яёa-z]+"
        r"(?:\s+[А-ЯЁA-Z]\.){0,2})",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bспециалист\s*"
        r"([А-ЯЁA-Z][а-яёa-z]+"
        r"(?:\s+[А-ЯЁA-Z]\.){0,2})",
        re.IGNORECASE,
    ),
]


def _normalize_year(year: int) -> int:
    if year < 100:
        return 2000 + year
    return year


def _format_date(day: int, month: int, year: int) -> str:
    normalized_year = _normalize_year(year)
    return date(normalized_year, month, day).isoformat()


def _extract_date(text: str) -> Optional[str]:
    match = NUMERIC_DATE_PATTERN.search(text)

    if match:
        day, month, year = map(int, match.groups())
        return _format_date(day, month, year)

    match = TEXT_DATE_PATTERN.search(text)

    if match:
        day = int(match.group(1))
        month = MONTHS[match.group(2).lower()]
        year = int(match.group(3)) if match.group(3) else date.today().year
        return _format_date(day, month, year)

    return None


def _extract_child_id(text: str) -> Optional[str]:
    match = CHILD_ID_PATTERN.search(text)

    if not match:
        return None

    return f"CH-{match.group(1)}"


def _extract_author(text: str) -> Optional[str]:
    for pattern in AUTHOR_PATTERNS:
        match = pattern.search(text)

        if match:
            return " ".join(match.group(1).split())

    return None


def _sleep_search_text(text: str) -> str:
    match = SLEEP_CONTEXT_PATTERN.search(text)

    if not match:
        return ""

    start = max(0, match.start() - 20)
    end = min(len(text), match.end() + 80)

    return text[start:end]


def _extract_sleep_hours(text: str) -> Optional[float]:
    context = _sleep_search_text(text)

    if not context:
        return None

    match = SLEEP_HOURS_MINUTES_PATTERN.search(context)

    if match:
        hours = float(match.group(1).replace(",", "."))
        minutes = int(match.group(2) or 0)

        return round(hours + minutes / 60, 2)

    match = SLEEP_DECIMAL_PATTERN.search(context)

    if match:
        return round(float(match.group(1).replace(",", ".")), 2)

    match = SLEEP_COLON_PATTERN.search(context)

    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))

        return round(hours + minutes / 60, 2)

    match = SLEEP_MINUTES_PATTERN.search(context)

    if match:
        return round(int(match.group(1)) / 60, 2)

    return None


def _extract_explicit_zone(text: str) -> Optional[str]:
    match = EXPLICIT_ZONE_PATTERN.search(text)

    if not match:
        return None

    return match.group(1).lower()


def extract(text: str) -> dict:
    """
    Extract structured information from a tutor record.

    Missing values are returned as None.
    """
    return {
        "date": _extract_date(text),
        "child_id": _extract_child_id(text),
        "author": _extract_author(text),
        "sleep_hours": _extract_sleep_hours(text),
        "zone": _extract_explicit_zone(text),
    }
