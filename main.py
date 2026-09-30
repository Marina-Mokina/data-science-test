import json
from pathlib import Path

from src.classifier import classify
from src.extractor import extract
from src.zone_checker import check_zone

DATASET_PATH = Path("dataset.json")
REPORT_PATH = Path("RESULTS.md")


def _format_value(value) -> str:
    """Format a value for Markdown."""
    if value is None:
        return "—"
    return str(value)


def _process_records(dataset: list[dict]) -> list[dict]:
    """Run extraction, classification and zone analysis."""
    results = []

    for record in dataset:
        result = {
            "id": record["id"],
            "text": record["text"],
        }

        if record["id"].startswith("R"):
            result["extracted"] = extract(record["text"])
            record_type, confidence = classify(record["text"])
            result["type"] = record_type
            result["type_confidence"] = confidence

        elif record["id"].startswith("Z"):
            is_related, confidence, reason = check_zone(record["text"])
            result["zone_analysis"] = {
                "is_related": is_related,
                "confidence": confidence,
                "reason": reason,
            }

        results.append(result)

    return results


def _build_report(results: list[dict]) -> str:
    """Build the RESULTS.md report."""
    lines = [
        "# Results",
        "",
        "## Part 1. Information extraction",
        "",
        "| ID | Date | Child ID | Author | Sleep, hours | Explicit zone |",
        "|---|---|---|---|---:|---|",
    ]

    for result in results:
        if not result["id"].startswith("R"):
            continue

        extracted = result["extracted"]

        lines.append(
            "| {id} | {date} | {child_id} | {author} | "
            "{sleep} | {zone} |".format(
                id=result["id"],
                date=_format_value(extracted["date"]),
                child_id=_format_value(extracted["child_id"]),
                author=_format_value(extracted["author"]),
                sleep=_format_value(extracted["sleep_hours"]),
                zone=_format_value(extracted["zone"]),
            )
        )

    lines.extend(
        [
            "",
            "## Part 2. Record classification",
            "",
            "| ID | Expected type | Predicted type | Confidence |",
            "|---|---|---|---:|",
        ]
    )

    expected_types = {
        "R1": "observation",
        "R2": "lesson_report",
        "R3": "parent_note",
        "R4": "observation",
        "R5": "recommendation",
        "R6": "observation",
    }

    for result in results:
        if not result["id"].startswith("R"):
            continue

        lines.append(
            "| {id} | {expected} | {predicted} | {confidence} |".format(
                id=result["id"],
                expected=expected_types[result["id"]],
                predicted=result["type"],
                confidence=result["type_confidence"],
            )
        )

    lines.extend(
        [
            "",
            "The classifier returns `unknown` when the difference "
            "between the two highest scores is below 0.15.",
            "",
            "## Part 3. Development zone analysis",
            "",
            "| ID | Observation | Related | Confidence | Reason |",
            "|---|---|---|---:|---|",
        ]
    )

    for result in results:
        if not result["id"].startswith("Z"):
            continue

        analysis = result["zone_analysis"]

        lines.append(
            "| {id} | {text} | {related} | {confidence} | {reason} |".format(
                id=result["id"],
                text=result["text"],
                related="yes" if analysis["is_related"] else "no",
                confidence=analysis["confidence"],
                reason=analysis["reason"],
            )
        )

    lines.extend(
        [
            "",
            "## Model",
            "",
            "Zone analysis was performed using the local "
            "`qwen2.5:7b-instruct` model through Ollama.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    results = _process_records(dataset)
    REPORT_PATH.write_text(_build_report(results), encoding="utf-8")

    print(f"Processed {len(results)} records.")
    print(f"Report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()
