from src.classifier import classify


def test_observation():
    record_type, confidence = classify(
        "Ребёнок был в хорошем настроении."
    )

    assert record_type == "observation"
    assert confidence > 0


def test_lesson_report():
    record_type, confidence = classify(
        "Отчёт о занятии №12 от 1 марта 2025 г."
    )

    assert record_type == "lesson_report"
    assert confidence >= 0.85


def test_parent_note():
    record_type, confidence = classify(
        "Мама ребёнка сообщила, что ночью просыпался."
    )

    assert record_type == "parent_note"
    assert confidence >= 0.90


def test_recommendation():
    record_type, confidence = classify(
        "Рекомендация: ввести сенсорную паузу."
    )

    assert record_type == "recommendation"
    assert confidence >= 0.90


def test_unknown():
    record_type, _ = classify(
        "Сегодня 12 градусов."
    )

    assert record_type == "unknown"
