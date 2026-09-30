import re
from typing import Dict, Tuple


UNKNOWN_THRESHOLD = 0.15
MAX_CONFIDENCE = 0.99
DEFAULT_CONFIDENCE = 0.35
OBSERVATION_SCORE = 0.30
LESSON_REPORT_SCORE = 0.85
PARENT_NOTE_SCORE = 0.90
RECOMMENDATION_SCORE = 0.90


TYPE_MARKERS: Dict[str, tuple[str, ...]] = {
    "observation": (
        "ребёнок",
        "ребенок",
        "тьютор",
        "тьют.",
        "наблюдение",
        "отвечал",
        "играл",
        "был",
        "была",
        "было",
        "отказался",
        "отказалась",
        "отказался идти",
        "наблюдал",
    ),
    "lesson_report": (
        "отчёт о занятии",
        "отчет о занятии",
        "отчёт занятия",
        "отчет занятия",
        "занятие №",
    ),
    "parent_note": (
        "мама ребёнка",
        "мама ребенка",
        "папа ребёнка",
        "папа ребенка",
        "родители",
    ),
    "recommendation": (
        "рекомендация",
        "рекомендуется",
        "ввести",
        "необходимо",
    ),
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def classify(text: str) -> Tuple[str, float]:
    """
    Classify a record into one of five predefined types.

    If the difference between the two highest scores is below
    UNKNOWN_THRESHOLD, return unknown.
    """
    normalized = _normalize(text)

    scores: Dict[str, float] = {
        record_type: 0.0
        for record_type in TYPE_MARKERS
    }

    for record_type, markers in TYPE_MARKERS.items():
        for marker in markers:
            if marker in normalized:
                if record_type == "observation":
                    scores[record_type] += OBSERVATION_SCORE
                elif record_type == "lesson_report":
                    scores[record_type] += LESSON_REPORT_SCORE
                elif record_type == "parent_note":
                    scores[record_type] += PARENT_NOTE_SCORE
                elif record_type == "recommendation":
                    scores[record_type] += RECOMMENDATION_SCORE

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    top_type, top_score = ranked[0]
    second_score = ranked[1][1]

    if top_score == 0:
        return "unknown", DEFAULT_CONFIDENCE

    if top_score - second_score < UNKNOWN_THRESHOLD:
        return "unknown", round(
            min(DEFAULT_CONFIDENCE, top_score),
            2,
        )

    confidence = min(top_score, MAX_CONFIDENCE)

    return top_type, round(confidence, 2)
