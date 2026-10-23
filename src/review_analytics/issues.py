"""Keyword-based candidate customer-issue analysis for app reviews."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "google_play_reviews_cleaned.csv"
DEFAULT_TABLES = PROJECT_ROOT / "outputs" / "tables"
DEFAULT_FIGURES = PROJECT_ROOT / "outputs" / "figures"
MISSING = "<MISSING>"
REQUIRED_COLUMNS = {"app_name", "review_text"}
SAMPLE_SIZE_PER_APP_THEME = 1
THEME_TERMS = {
    "delivery_fulfilment": (
        "delivery",
        "deliver",
        "delivered",
        "delivering",
        "courier",
        "shipment",
        "shipping",
        "shipped",
        "parcel",
        "late delivery",
        "delivery delay",
        "delayed",
        "delay",
        "not received",
        "delivery boy",
        "delivery partner",
        "fulfilment",
        "fulfillment",
    ),
    "customer_support": (
        "customer service",
        "customer care",
        "customer support",
        "support team",
        "helpline",
        "help line",
        "call center",
        "call centre",
        "customer executive",
        "support executive",
        "customer agent",
    ),
    "refunds_cancellations": (
        "refund",
        "refunded",
        "refunds",
        "refunding",
        "cancel",
        "canceled",
        "cancelled",
        "cancellation",
        "cancellations",
        "return",
        "returned",
        "returning",
        "replacement",
        "replace",
    ),
    "app_functionality": (
        "crash",
        "crashes",
        "crashing",
        "bug",
        "bugs",
        "error",
        "errors",
        "not working",
        "does not work",
        "doesn't work",
        "won't open",
        "not opening",
        "login",
        "log in",
        "loading",
        "stuck",
        "freeze",
        "frozen",
        "glitch",
        "glitches",
        "hangs",
        "hanging",
    ),
    "product_quality": (
        "poor quality",
        "bad quality",
        "quality issue",
        "quality issues",
        "product quality",
        "material quality",
        "damaged",
        "defective",
        "broken item",
        "broken product",
        "fake product",
        "counterfeit",
        "wrong product",
        "wrong item",
        "size issue",
        "size problem",
    ),
    "payment_issues": (
        "payment",
        "paid",
        "transaction",
        "upi",
        "credit card",
        "debit card",
        "card declined",
        "wallet",
        "charged",
        "double charged",
        "billing",
        "cash on delivery",
    ),
}
THEME_LABELS = {
    "delivery_fulfilment": "Delivery and fulfilment",
    "customer_support": "Customer support",
    "refunds_cancellations": "Refunds and cancellations",
    "app_functionality": "App functionality",
    "product_quality": "Product quality",
    "payment_issues": "Payment issues",
}
_PATTERNS = {
    theme: tuple(
        re.compile(
            r"(?<!\w)" + re.escape(term).replace(r"\ ", r"\s+") + r"(?!\w)",
            re.IGNORECASE,
        )
        for term in terms
    )
    for theme, terms in THEME_TERMS.items()
}
_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_URL = re.compile(r"\b(?:https?://|www\.)\S+", re.IGNORECASE)
_HANDLE = re.compile(r"(?<!\w)@[A-Z0-9_.-]{2,}", re.IGNORECASE)
_PHONE = re.compile(r"(?<!\w)\+?\d[\d\s().-]{5,}\d(?!\w)")
_ORDER_REFERENCE = re.compile(
    r"\b(?:order|tracking|transaction|reference|ref)\s*"
    r"(?:id|no\.?|number|#)?\s*[:#-]?\s*[A-Z0-9-]{5,}\b",
    re.IGNORECASE,
)
_PERSONAL_INTRO = re.compile(
    r"\b(?:my name is|name is|i am|i'm|contact me at|call me at|email me at)"
    r"\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?",
    re.IGNORECASE,
)


def _app_name(value: str | None) -> str:
    return value.strip() if value is not None and value.strip() else MISSING


def match_themes(review_text: str | None) -> tuple[str, ...]:
    """Return themes whose configured keyword patterns occur in review text."""
    if not review_text:
        return ()
    return tuple(
        theme
        for theme, patterns in _PATTERNS.items()
        if any(pattern.search(review_text) for pattern in patterns)
    )


def sanitize_sample_text(review_text: str) -> str:
    """Redact common contact and order identifiers from validation samples."""
    text = _EMAIL.sub("[redacted email]", review_text)
    text = _URL.sub("[redacted URL]", text)
    text = _HANDLE.sub("[redacted handle]", text)
    text = _ORDER_REFERENCE.sub("[redacted reference]", text)
    text = _PHONE.sub("[redacted number]", text)
    text = _PERSONAL_INTRO.sub("[redacted personal detail]", text)
    return " ".join(text.split())[:500]


def analyze_rows(
    rows: Iterable[Mapping[str, str | None]],
    sample_size_per_app_theme: int = SAMPLE_SIZE_PER_APP_THEME,
) -> dict[str, Any]:
    """Count overlapping keyword candidates with explicit denominators."""
    if sample_size_per_app_theme < 0:
        raise ValueError("sample_size_per_app_theme cannot be negative.")

    theme_counts: Counter[str] = Counter()
    app_counts: Counter[str] = Counter()
    app_theme_counts: dict[str, Counter[str]] = defaultdict(Counter)
    theme_sample_counts: dict[tuple[str, str], int] = defaultdict(int)
    samples_by_row: dict[int, dict[str, Any]] = {}
    blank_text_count = 0
    total_rows = 0

    for row_number, row in enumerate(rows, start=1):
        missing_columns = REQUIRED_COLUMNS - set(row)
        if missing_columns:
            raise ValueError(
                f"Row {row_number} is missing required columns: "
                f"{sorted(missing_columns)}"
            )
        if any(value is None for value in row.values()):
            raise ValueError(f"Row {row_number} has fewer fields than the header.")

        total_rows += 1
        app = _app_name(row.get("app_name"))
        text = row.get("review_text") or ""
        app_counts[app] += 1
        if not text.strip():
            blank_text_count += 1
            themes: tuple[str, ...] = ()
        else:
            themes = match_themes(text)

        for theme in themes:
            theme_counts[theme] += 1
            app_theme_counts[app][theme] += 1
            key = (app, theme)
            if theme_sample_counts[key] < sample_size_per_app_theme:
                theme_sample_counts[key] += 1
                sample = samples_by_row.setdefault(
                    row_number,
                    {
                        "source_row": row_number,
                        "app_name": app,
                        "review_text_redacted": sanitize_sample_text(text),
                        "candidate_themes": set(),
                        "validation_status": "candidate; human validation pending",
                    },
                )
                sample["candidate_themes"].add(theme)

    theme_rows = []
    for theme in THEME_TERMS:
        count = theme_counts[theme]
        theme_rows.append(
            {
                "theme": theme,
                "theme_label": THEME_LABELS[theme],
                "keyword_candidate_reviews": count,
                "dataset_review_denominator": total_rows,
                "percent_of_all_reviews": (
                    round(100 * count / total_rows, 2) if total_rows else 0.0
                ),
                "manual_validation_status": "not validated",
            }
        )

    apps = sorted(app_counts)
    app_theme_rows = []
    for app in apps:
        for theme in THEME_TERMS:
            count = app_theme_counts[app][theme]
            denominator = app_counts[app]
            app_theme_rows.append(
                {
                    "app_name": app,
                    "theme": theme,
                    "theme_label": THEME_LABELS[theme],
                    "keyword_candidate_reviews": count,
                    "app_review_denominator": denominator,
                    "percent_of_app_reviews": (
                        round(100 * count / denominator, 2) if denominator else 0.0
                    ),
                    "manual_validation_status": "not validated",
                }
            )

    samples = []
    for sample in samples_by_row.values():
        samples.append(
            {
                **sample,
                "candidate_themes": "|".join(
                    theme for theme in THEME_TERMS if theme in sample["candidate_themes"]
                ),
            }
        )

    return {
        "total_reviews": total_rows,
        "blank_review_text": blank_text_count,
        "app_counts": dict(app_counts),
        "themes": theme_rows,
        "themes_by_app": app_theme_rows,
        "samples": samples,
        "overlap_note": "Theme counts are overlapping; percentages may sum above 100%.",
    }


def _write_csv_exclusive(
    path: Path,
    fieldnames: list[str],
    rows: Iterable[Mapping[str, Any]],
) -> None:
    with path.open("x", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_figures(
    summary: dict[str, Any],
    figures_dir: Path,
) -> list[Path]:
    paths: list[Path] = []
    themes = summary["themes"]
    names = [row["theme_label"] for row in themes]
    values = [row["keyword_candidate_reviews"] for row in themes]
    percentages = [row["percent_of_all_reviews"] for row in themes]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(names, values, color="#4472C4")
    ax.invert_yaxis()
    ax.set(
        title="Keyword-Detected Candidate Issue Themes",
        xlabel="Reviews containing one or more theme keywords",
        ylabel="Candidate theme",
    )
    ax.bar_label(bars, labels=[f"{v:,} ({p:.1f}%)" for v, p in zip(values, percentages)])
    fig.tight_layout()
    path = figures_dir / "issue_theme_prevalence.png"
    with path.open("xb") as file:
        fig.savefig(file, format="png", dpi=160)
    plt.close(fig)
    paths.append(path)

    apps = sorted(summary["app_counts"])
    theme_keys = [row["theme"] for row in themes]
    theme_labels = [row["theme_label"] for row in themes]
    row_lookup = {
        (row["app_name"], row["theme"]): row
        for row in summary["themes_by_app"]
    }
    x_positions = list(range(len(apps)))
    width = 0.8 / max(len(theme_keys), 1)
    fig, ax = plt.subplots(figsize=(13, 6))
    palette = plt.get_cmap("tab10")
    for theme_index, (theme, label) in enumerate(zip(theme_keys, theme_labels)):
        offsets = [
            position - 0.4 + width * (theme_index + 0.5)
            for position in x_positions
        ]
        heights = [
            row_lookup[(app, theme)]["percent_of_app_reviews"] for app in apps
        ]
        ax.bar(
            offsets,
            heights,
            width=width,
            label=label,
            color=palette(theme_index),
        )
    ax.set_xticks(x_positions, apps, rotation=15)
    ax.set(
        title="Keyword-Detected Candidate Themes by App",
        xlabel="App",
        ylabel="Percent of app reviews containing theme keywords",
    )
    ax.legend(title="Candidate theme", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    path = figures_dir / "issue_theme_by_app.png"
    with path.open("xb") as file:
        fig.savefig(file, format="png", dpi=160)
    plt.close(fig)
    paths.append(path)
    return paths


def run_issue_analysis(
    input_path: str | Path = DEFAULT_INPUT,
    tables_dir: str | Path = DEFAULT_TABLES,
    figures_dir: str | Path = DEFAULT_FIGURES,
    sample_size_per_app_theme: int = SAMPLE_SIZE_PER_APP_THEME,
) -> dict[str, Any]:
    """Read the cleaned dataset and write issue-theme tables and figures."""
    source = Path(input_path)
    if not source.is_file():
        raise FileNotFoundError(f"Input dataset not found: {source}")

    tables_path = Path(tables_dir)
    figures_path = Path(figures_dir)
    output_paths = [
        tables_path / "issue_theme_counts.csv",
        tables_path / "issue_theme_by_app.csv",
        tables_path / "issue_review_sample.csv",
        figures_path / "issue_theme_prevalence.png",
        figures_path / "issue_theme_by_app.png",
    ]
    existing_paths = [str(path) for path in output_paths if path.exists()]
    if existing_paths:
        raise FileExistsError(
            "Refusing to overwrite existing issue-analysis outputs: "
            + ", ".join(existing_paths)
        )

    rows: list[dict[str, str]] = []
    with source.open("r", encoding="utf-8-sig", errors="strict", newline="") as file:
        reader = csv.DictReader(file, strict=True)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header.")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Input CSV is missing columns: {sorted(missing)}")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("Input CSV contains duplicate column names.")
        for row_number, row in enumerate(reader, start=1):
            if None in row:
                raise ValueError(f"Record {row_number} has more fields than the header.")
            if any(value is None for value in row.values()):
                raise ValueError(f"Record {row_number} has fewer fields than the header.")
            rows.append(row)

    summary = analyze_rows(rows, sample_size_per_app_theme)
    tables_path.mkdir(parents=True, exist_ok=True)
    figures_path.mkdir(parents=True, exist_ok=True)
    _write_csv_exclusive(
        output_paths[0],
        [
            "theme",
            "theme_label",
            "keyword_candidate_reviews",
            "dataset_review_denominator",
            "percent_of_all_reviews",
            "manual_validation_status",
        ],
        summary["themes"],
    )
    _write_csv_exclusive(
        output_paths[1],
        [
            "app_name",
            "theme",
            "theme_label",
            "keyword_candidate_reviews",
            "app_review_denominator",
            "percent_of_app_reviews",
            "manual_validation_status",
        ],
        summary["themes_by_app"],
    )
    _write_csv_exclusive(
        output_paths[2],
        [
            "source_row",
            "app_name",
            "candidate_themes",
            "review_text_redacted",
            "validation_status",
        ],
        summary["samples"],
    )
    _write_figures(summary, figures_path)
    summary["input"] = str(source)
    summary["table_paths"] = [str(path) for path in output_paths[:3]]
    summary["figure_paths"] = [str(path) for path in output_paths[3:]]
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--tables-dir", type=Path, default=DEFAULT_TABLES)
    parser.add_argument("--figures-dir", type=Path, default=DEFAULT_FIGURES)
    parser.add_argument(
        "--sample-size-per-app-theme",
        type=int,
        default=SAMPLE_SIZE_PER_APP_THEME,
    )
    arguments = parser.parse_args()
    summary = run_issue_analysis(
        arguments.input,
        arguments.tables_dir,
        arguments.figures_dir,
        arguments.sample_size_per_app_theme,
    )
    console_summary = {
        key: value
        for key, value in summary.items()
        if key != "samples"
    }
    console_summary["sample_count"] = len(summary["samples"])
    print(json.dumps(console_summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
