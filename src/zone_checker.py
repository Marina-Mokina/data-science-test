import json
from typing import Tuple

from openai import OpenAI


MODEL_NAME = "qwen2.5:7b-instruct"
OLLAMA_BASE_URL = "http://localhost:11434/v1"

ZONES = (
    "эмоции",
    "коммуникация",
    "поведение",
    "питание",
    "сенсорика",
    "сон",
    "моторика",
    "самообслуживание",
)

FALLBACK_KEYWORDS = {
    "эмоции": (
        "плакал",
        "плакала",
        "веселый",
        "весёлый",
        "грустный",
        "настроение",
    ),
    "коммуникация": (
        "не отвечал",
        "не отвечает",
        "речь",
        "обращенную речь",
        "обращённую речь",
    ),
    "поведение": (
        "ударил",
        "ударил себя",
        "отказался идти",
        "агресс",
    ),
    "питание": (
        "еда",
        "еду",
        "еды",
        "завтрак",
        "питание",
    ),
    "сенсорика": (
        "уши",
        "шум",
        "перегрузка",
        "сенсор",
    ),
    "сон": (
        "сон",
        "сна",
        "спал",
        "заснул",
        "ночью",
    ),
    "моторика": (
        "карандаш",
        "роняет",
        "мелкие предметы",
        "бегал",
    ),
    "самообслуживание": (
        "застегнул",
        "застегнуть",
        "куртку",
    ),
}

SYSTEM_PROMPT = """
Ты анализируешь краткие наблюдения тьютора о ребёнке.

Нужно определить, относится ли наблюдение к одной из отслеживаемых зон:
- эмоции
- коммуникация
- поведение
- питание
- сенсорика
- сон
- моторика
- самообслуживание

Если наблюдение не относится ни к одной зоне, верни is_related=false
и zone=null.

Если относится, выбери только одну наиболее подходящую зону.

Важно:
- поле reason должно быть написано только на русском языке;
- не додумывай информацию;
- учитывай только то, что явно следует из текста;
- бытовое событие само по себе не является наблюдением о развитии;
- если связь с зоной недостаточно очевидна, используй is_related=false;
- отвечай только на русском языке;
- поле confidence обязательно;
- confidence должно быть числом от 0 до 1;
- не пиши рассуждения;
- ответ должен содержать только один валидный JSON-объект.

Верни JSON строго в следующем формате:

{
  "is_related": true или false,
  "zone": "одна из зон или null",
  "confidence": число от 0 до 1,
  "reason": "краткое объяснение на русском языке"
}
""".strip()


def _get_client() -> OpenAI:
    """Create a client for the local Ollama server."""
    return OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key="ollama",
    )


def _parse_response(content: str) -> dict:
    """Parse and validate the JSON response from the LLM."""
    if content is None:
        raise RuntimeError(
            "LLM returned empty content. "
            "Check that Ollama is running and the model is available."
        )

    content = content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"LLM returned invalid JSON: {content}"
        ) from error

    if "is_related" not in result or "zone" not in result:
        raise RuntimeError(
            "LLM response does not contain required fields."
        )

    if result["zone"] not in ZONES and result["zone"] is not None:
        raise RuntimeError(
            f"Unknown zone returned by LLM: {result['zone']}"
        )

    if "confidence" not in result:
        raise RuntimeError(
            "LLM response does not contain required field: confidence."
        )

    confidence = float(result["confidence"])

    if not 0 <= confidence <= 1:
        raise RuntimeError(
            "Confidence must be between 0 and 1."
        )

    reason = result.get(
        "reason",
        "Зона не определена."
        if not result["is_related"]
        else "Наблюдение относится к отслеживаемой зоне.",
    )

    return {
        "is_related": bool(result["is_related"]),
        "zone": result["zone"],
        "confidence": round(confidence, 2),
        "reason": str(reason),
    }


def _fallback_check_zone(note: str) -> Tuple[bool, float, str]:
    """Check the development zone using keyword matching."""
    normalized = note.lower()

    for zone, keywords in FALLBACK_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized:
                return (
                    True,
                    0.70,
                    f"Наблюдение относится к зоне «{zone}» "
                    f"по ключевому слову «{keyword}».",
                )

    return False, 0.50, "Зона не определена."


def check_zone(note: str) -> Tuple[bool, float, str]:
    """Analyze an observation with a local Ollama instruction LLM.

    If the LLM is unavailable or returns an invalid response,
    a keyword-based fallback is used.

    Returns:
        Tuple containing:
        - whether the observation belongs to a tracked zone;
        - confidence score;
        - short explanation.
    """
    client = _get_client()

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"Наблюдение:\n{note}",
                },
            ],
            temperature=0.0,
            max_tokens=300,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        result = _parse_response(content)

        return (
            result["is_related"],
            result["confidence"],
            result["reason"],
        )

    except Exception:
        return _fallback_check_zone(note)
