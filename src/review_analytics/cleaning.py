"""Conservative, reproducible cleaning for the review text field."""

from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
import unicodedata
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "google_play_reviews_processed.csv"
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "data" / "processed" / "google_play_reviews_cleaned.csv"
)


def clean_text(text: str | None) -> str:
    """Normalize Unicode to NFC, lowercase, and standardize whitespace.

    Missing or whitespace-only input becomes an empty string. No tokens,
    punctuation, numbers, negation, or URLs are removed.
    """
    if text is None:
        return ""
    normalized = unicodedata.normalize("NFC", text)
    return " ".join(normalized.lower().split())


def clean_csv(
    input_path: str | Path = DEFAULT_INPUT,
    output_path: str | Path = DEFAULT_OUTPUT,
) -> dict[str, Any]:
    """Create a cleaned CSV without modifying the input or overwriting output."""
    source = Path(input_path).resolve(strict=True)
    destination = Path(output_path).resolve()

    if source == destination:
        raise ValueError("Input and output paths must be different.")
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    row_count = 0
    blank_review_text = 0
    changed_text = 0

    try:
        with source.open(
            "r", encoding="utf-8-sig", errors="strict", newline=""
        ) as source_file:
            reader = csv.DictReader(source_file, strict=True)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                raise ValueError("Input CSV has no header.")
            if len(fieldnames) != len(set(fieldnames)):
                raise ValueError("Input CSV contains duplicate column names.")
            if "review_text" not in fieldnames:
                raise ValueError("Input CSV is missing required column 'review_text'.")
            if "clean_text_new" in fieldnames:
                raise ValueError(
                    "Input already contains 'clean_text_new'; refusing to duplicate it."
                )

            output_fields = [*fieldnames, "clean_text_new"]
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                dir=destination.parent,
                prefix=f".{destination.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                writer = csv.DictWriter(
                    temporary_file,
                    fieldnames=output_fields,
                    extrasaction="raise",
                    lineterminator="\n",
                )
                writer.writeheader()

                for row_count, row in enumerate(reader, start=1):
                    if None in row:
                        raise ValueError(
                            f"Record {row_count} has more fields than the header."
                        )
                    if any(value is None for value in row.values()):
                        raise ValueError(
                            f"Record {row_count} has fewer fields than the header."
                        )

                    original_text = row["review_text"]
                    cleaned_text = clean_text(original_text)
                    blank_review_text += int(not original_text.strip())
                    changed_text += int(cleaned_text != original_text)
                    row["clean_text_new"] = cleaned_text
                    writer.writerow(row)

            # Hard-link creation fails rather than replacing an output that
            # appeared after the initial existence check.
            os.link(temporary_path, destination)
            temporary_path.unlink()
            temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return {
        "input": str(source),
        "output": str(destination),
        "rows_written": row_count,
        "blank_review_text": blank_review_text,
        "changed_text": changed_text,
        "original_columns_preserved": len(fieldnames),
        "output_columns": len(output_fields),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    print(json.dumps(clean_csv(arguments.input, arguments.output), indent=2))


if __name__ == "__main__":
    main()
