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
- не додумывай информацию;
- учитывай только то, что явно следует из текста;
- бытовое событие само по себе не является наблюдением о развитии;
- если связь с зоной недостаточно очевидна, используй is_related=false;
- не пиши рассуждения;
- отвечай только на русском языке;
- поле reason должно быть написано только на русском языке;
- ответ должен содержать только один валидный JSON-объект.

Верни JSON строго в следующем формате:

{
  "is_related": true или false,
  "zone": "одна из зон или null",
  "confidence": число от 0 до 1,
  "reason": "краткое объяснение"
}
""".strip()


def _get_client() -> OpenAI:
    """
    Create a client for the local Ollama server.
    """
    return OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key="ollama",
    )


def _parse_response(content: str) -> dict:
    """
    Parse and validate the JSON response from the LLM.
    """
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

    confidence = result.get("confidence", 0.5)
    confidence = float(confidence)

    if not 0 <= confidence <= 1:
        raise RuntimeError(
            "Confidence must be between 0 and 1."
        )

    reason = result.get(
        "reason",
        "Зона не определена." if not result["is_related"]
        else "Наблюдение относится к отслеживаемой зоне.",
    )

    return {
        "is_related": bool(result["is_related"]),
        "zone": result["zone"],
        "confidence": round(confidence, 2),
        "reason": str(reason),
    }


def check_zone(note: str) -> Tuple[bool, float, str]:
    """
    Analyze an observation with a local Ollama instruction LLM.

    Args:
        note: Tutor observation.

    Returns:
        Tuple containing:
        - whether the observation belongs to a tracked zone;
        - confidence score;
        - short explanation.
    """
    client = _get_client()

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
