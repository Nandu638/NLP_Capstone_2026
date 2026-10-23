"""Reproducible text-only sentiment-label classification experiment."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = (
    PROJECT_ROOT / "data" / "processed" / "google_play_reviews_cleaned.csv"
)
DEFAULT_RESULTS = PROJECT_ROOT / "outputs" / "tables" / "sentiment_model_results.json"
RANDOM_SEED = 42
TEST_SIZE = 0.2
TEXT_COLUMN = "clean_text_new"
TARGET_COLUMN = "sentiment"


def stratified_split(
    texts: Sequence[str],
    labels: Sequence[str],
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_SEED,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Return deterministic stratified train/test text and label partitions."""
    if len(texts) != len(labels):
        raise ValueError("Texts and labels must have the same number of rows.")
    if len(set(labels)) < 2:
        raise ValueError("At least two target classes are required.")
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        list(texts),
        list(labels),
        test_size=test_size,
        random_state=random_state,
        stratify=list(labels),
    )
    return train_texts, test_texts, train_labels, test_labels


def build_text_pipeline(random_state: int = RANDOM_SEED) -> Pipeline:
    """Build a TF-IDF and Logistic Regression text-only pipeline."""
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=False,
                    ngram_range=(1, 2),
                    min_df=1,
                    max_features=50_000,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1_000,
                    random_state=random_state,
                ),
            ),
        ]
    )


def calculate_metrics(
    true_labels: Sequence[str],
    predicted_labels: Sequence[str],
    labels: Sequence[str],
) -> dict[str, Any]:
    """Calculate accuracy, macro and per-class metrics, and confusion matrix."""
    if len(true_labels) != len(predicted_labels):
        raise ValueError("True and predicted label sequences must have equal length.")
    if not true_labels:
        raise ValueError("Metrics require at least one test record.")
    precision, recall, f1, support = precision_recall_fscore_support(
        true_labels,
        predicted_labels,
        labels=list(labels),
        zero_division=0,
    )
    return {
        "accuracy": round(float(accuracy_score(true_labels, predicted_labels)), 6),
        "macro_precision": round(
            float(
                precision_recall_fscore_support(
                    true_labels,
                    predicted_labels,
                    labels=list(labels),
                    average="macro",
                    zero_division=0,
                )[0]
            ),
            6,
        ),
        "macro_recall": round(
            float(
                precision_recall_fscore_support(
                    true_labels,
                    predicted_labels,
                    labels=list(labels),
                    average="macro",
                    zero_division=0,
                )[1]
            ),
            6,
        ),
        "macro_f1": round(
            float(
                precision_recall_fscore_support(
                    true_labels,
                    predicted_labels,
                    labels=list(labels),
                    average="macro",
                    zero_division=0,
                )[2]
            ),
            6,
        ),
        "per_class": {
            label: {
                "precision": round(float(precision[index]), 6),
                "recall": round(float(recall[index]), 6),
                "f1": round(float(f1[index]), 6),
                "support": int(support[index]),
            }
            for index, label in enumerate(labels)
        },
        "confusion_matrix": {
            "labels": list(labels),
            "rows_true_columns_predicted": confusion_matrix(
                true_labels, predicted_labels, labels=list(labels)
            ).tolist(),
        },
        "class_support": {
            label: int(support[index]) for index, label in enumerate(labels)
        },
    }


def _read_dataset(path: Path) -> tuple[list[str], list[str], int]:
    texts: list[str] = []
    labels: list[str] = []
    with path.open("r", encoding="utf-8-sig", errors="strict", newline="") as file:
        reader = csv.DictReader(file, strict=True)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header.")
        missing_columns = {TEXT_COLUMN, TARGET_COLUMN} - set(reader.fieldnames)
        if missing_columns:
            raise ValueError(f"Input CSV is missing columns: {sorted(missing_columns)}")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("Input CSV contains duplicate column names.")
        for row_number, row in enumerate(reader, start=1):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Record {row_number} has a malformed field count.")
            text = row[TEXT_COLUMN]
            label = row[TARGET_COLUMN]
            if not text.strip():
                raise ValueError(f"Record {row_number} has blank {TEXT_COLUMN}.")
            if not label.strip():
                raise ValueError(f"Record {row_number} has blank {TARGET_COLUMN}.")
            texts.append(text)
            labels.append(label)
    if not texts:
        raise ValueError("Input CSV contains no data records.")
    return texts, labels, len(texts)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_experiment(
    input_path: str | Path = DEFAULT_INPUT,
    results_path: str | Path = DEFAULT_RESULTS,
) -> dict[str, Any]:
    """Run stratified majority and TF-IDF Logistic Regression evaluation."""
    source = Path(input_path).resolve(strict=True)
    destination = Path(results_path).resolve()
    if source == destination:
        raise ValueError("Input and results paths must be different.")
    if destination.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing results file: {destination}"
        )

    texts, labels, total_rows = _read_dataset(source)
    label_order = sorted(set(labels))
    train_texts, test_texts, train_labels, test_labels = stratified_split(
        texts, labels
    )

    train_counts = Counter(train_labels)
    majority_label = sorted(
        train_counts, key=lambda label: (-train_counts[label], label)
    )[0]
    majority_predictions = [majority_label] * len(test_labels)
    pipeline = build_text_pipeline()
    pipeline.fit(train_texts, train_labels)
    classifier_predictions = pipeline.predict(test_texts).tolist()

    result = {
        "experiment": {
            "input": str(source),
            "input_sha256": _sha256(source),
            "rows": total_rows,
            "text_column": TEXT_COLUMN,
            "target_column": TARGET_COLUMN,
            "features_used": [TEXT_COLUMN],
            "metadata_features_used": [],
            "split": {
                "method": "stratified train_test_split",
                "test_size": TEST_SIZE,
                "random_state": RANDOM_SEED,
                "train_rows": len(train_texts),
                "test_rows": len(test_texts),
                "train_class_counts": dict(sorted(train_counts.items())),
                "test_class_counts": dict(sorted(Counter(test_labels).items())),
            },
            "target_note": (
                "The existing sentiment labels align perfectly with ratings "
                "(ratings 1-2 negative, 3 neutral, 4-5 positive); historical "
                "label provenance is unverified. Metrics measure agreement "
                "with these existing labels, not independently validated "
                "customer sentiment."
            ),
        },
        "models": {
            "majority_class_baseline": {
                "settings": {
                    "prediction": "most frequent training label",
                    "tie_break": "lexicographically smallest label",
                    "selected_training_label": majority_label,
                },
                "metrics": calculate_metrics(
                    test_labels, majority_predictions, label_order
                ),
            },
            "tfidf_logistic_regression": {
                "settings": {
                    "tfidf": {
                        "ngram_range": [1, 2],
                        "min_df": 1,
                        "max_features": 50_000,
                        "sublinear_tf": True,
                        "lowercase": False,
                    },
                    "logistic_regression": {
                        "max_iter": 1_000,
                        "random_state": RANDOM_SEED,
                        "class_weight": None,
                    },
                    "vectorizer_fitted_on": "training partition only",
                },
                "metrics": calculate_metrics(
                    test_labels, classifier_predictions, label_order
                ),
            },
        },
        "label_order": label_order,
    }

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
        file.write("\n")
    result["results_path"] = str(destination)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    arguments = parser.parse_args()
    print(json.dumps(run_experiment(arguments.input, arguments.results), indent=2))


if __name__ == "__main__":
    main()
