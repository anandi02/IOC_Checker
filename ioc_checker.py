
import csv
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
INPUT_FILE = PROJECT_DIR / "sample_indicators.csv"
KNOWN_FILE = PROJECT_DIR / "known_iocs.csv"
OUTPUT_FILE = PROJECT_DIR / "ioc_results.csv"


def load_iocs(file_path):
    """Load known indicators from a CSV file."""
    indicators = set()

    with file_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames or "type" not in reader.fieldnames or "value" not in reader.fieldnames:
            raise ValueError(
                f"{file_path.name} must contain 'type' and 'value' columns."
            )

        for row in reader:
            indicator_type = (row.get("type") or "").strip().lower()
            value = (row.get("value") or "").strip().lower()

            if indicator_type and value:
                indicators.add((indicator_type, value))

    return indicators


def main():
    if not INPUT_FILE.exists() or not KNOWN_FILE.exists():
        print("Error: CSV files not found.")
        print("Create sample_indicators.csv and known_iocs.csv first.")
        return

    try:
        known_iocs = load_iocs(KNOWN_FILE)

        with INPUT_FILE.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames or not {"type", "value"}.issubset(reader.fieldnames):
                print("Error: sample_indicators.csv needs type and value columns.")
                return

            results = []

            for row in reader:
                indicator_type = (row.get("type") or "").strip().lower()
                value = (row.get("value") or "").strip().lower()

                if not indicator_type or not value:
                    continue

                matched = (indicator_type, value) in known_iocs

                results.append({
                    "type": indicator_type,
                    "value": value,
                    "result": "MATCH - REVIEW" if matched else "NO MATCH",
                })

    except (OSError, csv.Error, ValueError) as error:
        print(f"Could not process CSV files: {error}")
        return

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        fieldnames = ["type", "value", "result"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    matches = sum(
        result["result"] == "MATCH - REVIEW"
        for result in results
    )

    print("===== IOC CHECKER REPORT =====")
    print(f"Indicators checked: {len(results)}")
    print(f"Matches requiring review: {matches}")
    print(f"No matches: {len(results) - matches}")

    for result in results:
        print(
            f"{result['type']} | {result['value']} | {result['result']}"
        )

    print(f"\nResults saved to: {OUTPUT_FILE}")
    print("A match is a lead for investigation, not proof of compromise.")


if __name__ == "__main__":
    main()

