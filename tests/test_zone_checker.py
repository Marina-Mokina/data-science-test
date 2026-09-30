import pytest

from src.zone_checker import _parse_response


def test_valid_llm_response():
    response = """
    {
        "is_related": true,
        "zone": "сенсорика",
        "confidence": 0.91,
        "reason": "Ребёнок закрыл уши из-за шума."
    }
    """

    result = _parse_response(response)

    assert result["is_related"] is True
    assert result["zone"] == "сенсорика"
    assert result["confidence"] == 0.91


def test_unrelated_observation():
    response = """
    {
        "is_related": false,
        "zone": null,
        "confidence": 0.95,
        "reason": "В тексте нет наблюдения, относящегося к зоне."
    }
    """

    result = _parse_response(response)

    assert result["is_related"] is False
    assert result["zone"] is None


def test_invalid_zone():
    response = """
    {
        "is_related": true,
        "zone": "учёба",
        "confidence": 0.8,
        "reason": "Причина."
    }
    """

    with pytest.raises(RuntimeError):
        _parse_response(response)


def test_invalid_json():
    with pytest.raises(RuntimeError):
        _parse_response("not json")
