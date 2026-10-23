"""Descriptive, non-causal exploratory analysis for cleaned app reviews."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any, Iterable, Mapping

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "google_play_reviews_cleaned.csv"
DEFAULT_FIGURES = PROJECT_ROOT / "outputs" / "figures"
DEFAULT_TABLES = PROJECT_ROOT / "outputs" / "tables"
MISSING = "<MISSING>"
EXPECTED_APPS = ("Amazon Shopping", "Flipkart", "Myntra")
EXPECTED_RATINGS = ("1", "2", "3", "4", "5")
EXPECTED_SENTIMENTS = ("negative", "neutral", "positive")
REQUIRED_COLUMNS = {"app_name", "rating", "sentiment", "clean_text_new"}


def _category(value: str | None) -> str:
    return value.strip() if value is not None and value.strip() else MISSING


def _sorted_ratings(values: Iterable[str]) -> list[str]:
    unique = set(values)
    known = [rating for rating in EXPECTED_RATINGS if rating in unique]
    unexpected = sorted(
        (rating for rating in unique if rating not in EXPECTED_RATINGS and rating != MISSING),
        key=lambda value: (not value.lstrip("-").isdigit(), value),
    )
    if MISSING in unique:
        unexpected.append(MISSING)
    return known + unexpected


def _percentile(sorted_values: list[int], percentile: float) -> float | None:
    if not sorted_values:
        return None
    position = (len(sorted_values) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(sorted_values[lower])
    fraction = position - lower
    return sorted_values[lower] * (1 - fraction) + sorted_values[upper] * fraction


def _length_stats(values: list[int]) -> dict[str, float | int | None]:
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "mean": round(mean(ordered), 2) if ordered else None,
        "median": round(median(ordered), 2) if ordered else None,
        "p95": round(_percentile(ordered, 0.95), 2) if ordered else None,
        "min": ordered[0] if ordered else None,
        "max": ordered[-1] if ordered else None,
    }


def analyze_rows(rows: Iterable[Mapping[str, str | None]]) -> dict[str, Any]:
    """Calculate descriptive counts and text lengths without dropping rows."""
    app_counts: Counter[str] = Counter()
    rating_counts: Counter[str] = Counter()
    sentiment_counts: Counter[str] = Counter()
    rating_sentiment_counts: dict[str, Counter[str]] = defaultdict(Counter)
    app_rating_counts: dict[str, Counter[str]] = defaultdict(Counter)
    app_sentiment_counts: dict[str, Counter[str]] = defaultdict(Counter)
    lengths_by_app: dict[str, list[int]] = defaultdict(list)
    token_lengths_by_app: dict[str, list[int]] = defaultdict(list)
    character_lengths: list[int] = []
    token_lengths: list[int] = []
    missing_counts: Counter[str] = Counter()
    alignment_matched = 0
    alignment_conflicts = 0
    alignment_unassessable = 0
    total = 0

    for row_number, row in enumerate(rows, start=1):
        missing_columns = REQUIRED_COLUMNS - set(row)
        if missing_columns:
            raise ValueError(
                f"Row {row_number} is missing required columns: "
                f"{sorted(missing_columns)}"
            )
        if any(value is None for value in row.values()):
            raise ValueError(f"Row {row_number} has fewer fields than the header.")

        total += 1
        app = _category(row.get("app_name"))
        rating = _category(row.get("rating"))
        sentiment = _category(row.get("sentiment"))
        text = row.get("clean_text_new") or ""

        app_counts[app] += 1
        rating_counts[rating] += 1
        sentiment_counts[sentiment] += 1
        rating_sentiment_counts[rating][sentiment] += 1
        app_rating_counts[app][rating] += 1
        app_sentiment_counts[app][sentiment] += 1

        length = len(text)
        tokens = len(text.split())
        character_lengths.append(length)
        token_lengths.append(tokens)
        lengths_by_app[app].append(length)
        token_lengths_by_app[app].append(tokens)

        if app == MISSING:
            missing_counts["app_name"] += 1
        if rating == MISSING:
            missing_counts["rating"] += 1
        if sentiment == MISSING:
            missing_counts["sentiment"] += 1
        if not text.strip():
            missing_counts["clean_text_new"] += 1

        expected = (
            "negative"
            if rating in {"1", "2"}
            else "neutral"
            if rating == "3"
            else "positive"
            if rating in {"4", "5"}
            else None
        )
        if expected is None or sentiment == MISSING:
            alignment_unassessable += 1
        elif sentiment == expected:
            alignment_matched += 1
        else:
            alignment_conflicts += 1

    ratings = _sorted_ratings(rating_counts)
    sentiments = [
        *[value for value in EXPECTED_SENTIMENTS if value in sentiment_counts],
        *sorted(
            value
            for value in sentiment_counts
            if value not in EXPECTED_SENTIMENTS and value != MISSING
        ),
    ]
    if MISSING in sentiment_counts:
        sentiments.append(MISSING)
    apps = list(EXPECTED_APPS)
    apps.extend(sorted(app for app in app_counts if app not in EXPECTED_APPS))

    return {
        "row_count": total,
        "apps": apps,
        "ratings": ratings,
        "sentiments": sentiments,
        "app_counts": dict(app_counts),
        "rating_counts": dict(rating_counts),
        "sentiment_counts": dict(sentiment_counts),
        "rating_sentiment_counts": {
            rating: dict(counts) for rating, counts in rating_sentiment_counts.items()
        },
        "app_rating_counts": {
            app: dict(counts) for app, counts in app_rating_counts.items()
        },
        "app_sentiment_counts": {
            app: dict(counts) for app, counts in app_sentiment_counts.items()
        },
        "lengths": {
            "characters": _length_stats(character_lengths),
            "tokens": _length_stats(token_lengths),
        },
        "lengths_by_app": {
            app: _length_stats(values) for app, values in lengths_by_app.items()
        },
        "token_lengths_by_app": {
            app: _length_stats(values) for app, values in token_lengths_by_app.items()
        },
        "missing_counts": dict(missing_counts),
        "rating_sentiment_alignment": {
            "matched": alignment_matched,
            "conflicts": alignment_conflicts,
            "unassessable": alignment_unassessable,
        },
    }


def _write_csv(path: Path, fieldnames: list[str], rows: Iterable[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_tables(summary: dict[str, Any], tables_dir: Path) -> list[Path]:
    app_rows = [
        {"app_name": app, "record_count": summary["app_counts"].get(app, 0)}
        for app in summary["apps"]
    ]
    rating_rows = [
        {"rating": rating, "record_count": summary["rating_counts"].get(rating, 0)}
        for rating in summary["ratings"]
    ]
    app_rating_rows = [
        {
            "app_name": app,
            "rating": rating,
            "record_count": summary["app_rating_counts"].get(app, {}).get(rating, 0),
            "app_percent": round(
                100
                * summary["app_rating_counts"].get(app, {}).get(rating, 0)
                / summary["app_counts"].get(app, 1),
                2,
            ),
        }
        for app in summary["apps"]
        for rating in summary["ratings"]
    ]
    sentiment_rows = [
        {
            "sentiment": sentiment,
            "record_count": summary["sentiment_counts"].get(sentiment, 0),
        }
        for sentiment in summary["sentiments"]
    ]
    rating_sentiment_rows = [
        {
            "rating": rating,
            "sentiment": sentiment,
            "record_count": summary["rating_sentiment_counts"]
            .get(rating, {})
            .get(sentiment, 0),
        }
        for rating in summary["ratings"]
        for sentiment in summary["sentiments"]
    ]
    app_sentiment_rows = [
        {
            "app_name": app,
            "sentiment": sentiment,
            "record_count": summary["app_sentiment_counts"].get(app, {}).get(
                sentiment, 0
            ),
            "app_percent": round(
                100
                * summary["app_sentiment_counts"].get(app, {}).get(sentiment, 0)
                / summary["app_counts"].get(app, 1),
                2,
            ),
        }
        for app in summary["apps"]
        for sentiment in summary["sentiments"]
    ]
    length_rows = [
        {"scope": "all", "measure": "characters", **summary["lengths"]["characters"]},
        {"scope": "all", "measure": "tokens", **summary["lengths"]["tokens"]},
    ]
    for app in summary["apps"]:
        character_stats = summary["lengths_by_app"].get(app)
        token_stats = summary["token_lengths_by_app"].get(app)
        if character_stats is not None and token_stats is not None:
            length_rows.extend(
                [
                    {"scope": app, "measure": "characters", **character_stats},
                    {"scope": app, "measure": "tokens", **token_stats},
                ]
            )

    files_and_rows = [
        ("app_counts.csv", ["app_name", "record_count"], app_rows),
        ("rating_counts.csv", ["rating", "record_count"], rating_rows),
        (
            "app_rating_counts.csv",
            ["app_name", "rating", "record_count", "app_percent"],
            app_rating_rows,
        ),
        (
            "rating_sentiment_counts.csv",
            ["rating", "sentiment", "record_count"],
            rating_sentiment_rows,
        ),
        ("sentiment_counts.csv", ["sentiment", "record_count"], sentiment_rows),
        (
            "app_sentiment_counts.csv",
            ["app_name", "sentiment", "record_count", "app_percent"],
            app_sentiment_rows,
        ),
        (
            "review_length_summary.csv",
            ["scope", "measure", "count", "mean", "median", "p95", "min", "max"],
            length_rows,
        ),
    ]
    paths = []
    for filename, fieldnames, rows in files_and_rows:
        path = tables_dir / filename
        _write_csv(path, fieldnames, rows)
        paths.append(path)
    return paths


def _save_figures(
    rows: list[dict[str, str]],
    summary: dict[str, Any],
    figures_dir: Path,
) -> list[Path]:
    paths: list[Path] = []

    ratings = summary["ratings"]
    rating_counts = [summary["rating_counts"].get(value, 0) for value in ratings]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(ratings, rating_counts, color="#4472C4")
    ax.set(title="Review Rating Distribution", xlabel="Rating", ylabel="Reviews")
    ax.bar_label(ax.containers[0], fmt="%d")
    fig.tight_layout()
    path = figures_dir / "rating_distribution.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    paths.append(path)

    sentiments = summary["sentiments"]
    sentiment_counts = [
        summary["sentiment_counts"].get(value, 0) for value in sentiments
    ]
    fig, ax = plt.subplots(figsize=(8, 5))
    sentiment_colors = {
        "negative": "#C0504D",
        "neutral": "#A5A5A5",
        "positive": "#70AD47",
    }
    colors = [
        sentiment_colors.get(label, plt.get_cmap("tab10")(index % 10))
        for index, label in enumerate(sentiments)
    ]
    ax.bar(sentiments, sentiment_counts, color=colors)
    ax.set(title="Observed Sentiment Label Distribution", xlabel="Sentiment label", ylabel="Reviews")
    ax.bar_label(ax.containers[0], fmt="%d")
    fig.tight_layout()
    path = figures_dir / "sentiment_distribution.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    paths.append(path)

    apps = summary["apps"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    rating_colors = [
        plt.get_cmap("tab10")(index % 10) for index in range(len(ratings))
    ]
    app_positions = list(range(len(apps)))
    rating_width = 0.8 / max(len(ratings), 1)
    for rating_index, (rating, color) in enumerate(zip(ratings, rating_colors)):
        values = []
        for app in apps:
            total = summary["app_counts"].get(app, 0)
            count = summary["app_rating_counts"].get(app, {}).get(rating, 0)
            values.append(100 * count / total if total else 0)
        offsets = [
            position - 0.4 + rating_width * (rating_index + 0.5)
            for position in app_positions
        ]
        axes[0].bar(offsets, values, width=rating_width, label=f"Rating {rating}", color=color)
    axes[0].set(title="Rating Mix by App", ylabel="Share of app reviews (%)")
    axes[0].set_xticks(app_positions, apps, rotation=15)
    axes[0].legend(title="Rating")

    bottoms = [0.0] * len(apps)
    sentiment_colors = {"negative": "#C0504D", "neutral": "#A5A5A5", "positive": "#70AD47"}
    for sentiment in sentiments:
        values = []
        for app in apps:
            total = summary["app_counts"].get(app, 0)
            count = summary["app_sentiment_counts"].get(app, {}).get(sentiment, 0)
            values.append(100 * count / total if total else 0)
        axes[1].bar(
            apps,
            values,
            bottom=bottoms,
            label=sentiment,
            color=sentiment_colors.get(sentiment, "#8064A2"),
        )
        bottoms = [bottom + value for bottom, value in zip(bottoms, values)]
    axes[1].set(title="Rating-Aligned Sentiment Mix by App", ylabel="Share of app reviews (%)", ylim=(0, 100))
    axes[1].tick_params(axis="x", rotation=15)
    axes[1].legend(title="Observed label")
    fig.suptitle("Review Distribution Comparison Across Apps")
    fig.tight_layout()
    path = figures_dir / "app_comparison.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    paths.append(path)

    lengths_by_app = [
        [
            len(row["clean_text_new"])
            for row in rows
            if _category(row.get("app_name")) == app
        ]
        for app in apps
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    if lengths_by_app and any(lengths_by_app):
        ax.boxplot(lengths_by_app, tick_labels=apps, showfliers=False)
    else:
        ax.text(0.5, 0.5, "No review text lengths available", ha="center", va="center")
        ax.set_xticks([])
    ax.set(
        title="Review Text Length by App (Box Plot; Outliers Hidden)",
        xlabel="App",
        ylabel="Characters in clean_text_new",
    )
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    path = figures_dir / "review_length_by_app.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    paths.append(path)

    return paths


def run_eda(
    input_path: str | Path = DEFAULT_INPUT,
    figures_dir: str | Path = DEFAULT_FIGURES,
    tables_dir: str | Path = DEFAULT_TABLES,
) -> dict[str, Any]:
    """Read the cleaned CSV and write descriptive tables and figures."""
    source = Path(input_path)
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

    summary = analyze_rows(rows)
    figures_path = Path(figures_dir)
    tables_path = Path(tables_dir)
    figures_path.mkdir(parents=True, exist_ok=True)
    tables_path.mkdir(parents=True, exist_ok=True)
    summary["figure_paths"] = [
        str(path) for path in _save_figures(rows, summary, figures_path)
    ]
    summary["table_paths"] = [
        str(path) for path in _write_tables(summary, tables_path)
    ]
    summary["input"] = str(source)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--figures-dir", type=Path, default=DEFAULT_FIGURES)
    parser.add_argument("--tables-dir", type=Path, default=DEFAULT_TABLES)
    arguments = parser.parse_args()
    summary = run_eda(arguments.input, arguments.figures_dir, arguments.tables_dir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
