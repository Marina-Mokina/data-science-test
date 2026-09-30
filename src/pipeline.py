from typing import Any

from src.classifier import classify
from src.extractor import extract
from src.zone_checker import check_zone


def process_record(record: dict[str, Any]) -> dict[str, Any]:
    """
    Process one record through extraction, classification,
    and zone analysis.
    """
    text = record["text"]

    extracted = extract(text)
    record_type, type_confidence = classify(text)

    result = {
        "id": record["id"],
        "text": text,
        "extracted": extracted,
        "type": record_type,
        "type_confidence": type_confidence,
    }

    if record.get("type") == "observation":
        (
            is_related,
            zone_confidence,
            reason,
        ) = check_zone(text)

        result["zone_analysis"] = {
            "is_related": is_related,
            "confidence": zone_confidence,
            "reason": reason,
        }

    return result
