from src.extractor import extract


def test_numeric_date_and_sleep():
    text = (
        "05.03.2025. Ребёнок CH-0421, "
        "тьютор Иванова А. С. Сон 6 ч 30 мин."
    )

    result = extract(text)

    assert result["date"] == "2025-03-05"
    assert result["child_id"] == "CH-0421"
    assert result["author"] == "Иванова А. С."
    assert result["sleep_hours"] == 6.5


def test_text_date_and_decimal_sleep():
    text = (
        "Отчёт о занятии №12 от 1 марта 2025 г. "
        "Специалист Петров И. И. Ребёнок CH 0107, "
        "зона: моторика. Накануне спал 6,5 часов."
    )

    result = extract(text)

    assert result["date"] == "2025-03-01"
    assert result["child_id"] == "CH-0107"
    assert result["author"] == "Петров И. И."
    assert result["sleep_hours"] == 6.5
    assert result["zone"] == "моторика"


def test_colon_sleep():
    text = (
        "03/01/25, мама ребёнка CH-0342: "
        "ночью просыпался, итого 5:45 сна."
    )

    result = extract(text)

    assert result["date"] == "2025-01-03"
    assert result["child_id"] == "CH-0342"
    assert result["sleep_hours"] == 5.75


def test_minutes_sleep_and_short_author():
    text = (
        "07.03.25 ch-0421 тьют.Иванова "
        "сон~390 минут."
    )

    result = extract(text)

    assert result["date"] == "2025-03-07"
    assert result["child_id"] == "CH-0421"
    assert result["author"] == "Иванова"
    assert result["sleep_hours"] == 6.5


def test_missing_values_are_none():
    result = extract(
        "Ребёнок был в хорошем настроении."
    )

    assert result["date"] is None
    assert result["child_id"] is None
    assert result["author"] is None
    assert result["sleep_hours"] is None
    assert result["zone"] is None
