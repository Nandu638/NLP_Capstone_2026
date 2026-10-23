import csv
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from review_analytics.sentiment import (
    build_text_pipeline,
    calculate_metrics,
    run_experiment,
    stratified_split,
)


class SplitTests(unittest.TestCase):
    def test_split_is_deterministic_and_stratified(self):
        texts = [f"review class{label} sample{index}" for label in "abc" for index in range(10)]
        labels = [label for label in "abc" for _ in range(10)]

        first = stratified_split(texts, labels, test_size=0.3, random_state=7)
        second = stratified_split(texts, labels, test_size=0.3, random_state=7)

        self.assertEqual(first, second)
        train_texts, test_texts, train_labels, test_labels = first
        self.assertEqual(len(train_texts), 21)
        self.assertEqual(len(test_texts), 9)
        self.assertTrue(set(train_texts).isdisjoint(test_texts))
        self.assertEqual(Counter(test_labels), {"a": 3, "b": 3, "c": 3})
        self.assertEqual(len(train_labels), len(train_texts))


class PipelineTests(unittest.TestCase):
    def test_vectorizer_fits_training_text_only(self):
        pipeline = build_text_pipeline(random_state=5)
        train_texts = ["good helpful", "bad broken", "good fast", "bad slow"]
        train_labels = ["positive", "negative", "positive", "negative"]
        pipeline.fit(train_texts, train_labels)
        vocabulary = pipeline.named_steps["tfidf"].vocabulary_

        self.assertIn("good", vocabulary)
        self.assertNotIn("testonlytoken", vocabulary)
        prediction = pipeline.predict(["testonlytoken good"])
        self.assertEqual(len(prediction), 1)


class MetricTests(unittest.TestCase):
    def test_metrics_include_macro_per_class_confusion_and_support(self):
        result = calculate_metrics(
            ["negative", "negative", "positive", "positive"],
            ["negative", "positive", "positive", "positive"],
            ["negative", "positive"],
        )

        self.assertEqual(result["accuracy"], 0.75)
        self.assertEqual(result["macro_precision"], 0.833333)
        self.assertEqual(result["macro_recall"], 0.75)
        self.assertEqual(result["macro_f1"], 0.733333)
        self.assertEqual(
            result["confusion_matrix"]["rows_true_columns_predicted"],
            [[1, 1], [0, 2]],
        )
        self.assertEqual(result["class_support"], {"negative": 2, "positive": 2})
        self.assertEqual(result["per_class"]["negative"]["recall"], 0.5)


class ExperimentTests(unittest.TestCase):
    def test_experiment_saves_settings_and_metrics_without_metadata_features(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "reviews.csv"
            results_path = root / "results.json"
            columns = ["clean_text_new", "sentiment", "rating", "app_name"]
            rows = []
            for index in range(20):
                sentiment = "negative" if index < 10 else "positive"
                rows.append(
                    {
                        "clean_text_new": (
                            f"{sentiment} signal review number {index}"
                        ),
                        "sentiment": sentiment,
                        "rating": "1" if sentiment == "negative" else "5",
                        "app_name": "metadata must not become a feature",
                    }
                )
            with input_path.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=columns)
                writer.writeheader()
                writer.writerows(rows)

            result = run_experiment(input_path, results_path)
            saved = json.loads(results_path.read_text(encoding="utf-8"))

            self.assertEqual(result["experiment"]["rows"], 20)
            self.assertEqual(result["experiment"]["split"]["train_rows"], 16)
            self.assertEqual(result["experiment"]["split"]["test_rows"], 4)
            self.assertEqual(
                result["experiment"]["features_used"], ["clean_text_new"]
            )
            self.assertEqual(result["experiment"]["metadata_features_used"], [])
            self.assertIn("majority_class_baseline", saved["models"])
            self.assertIn("tfidf_logistic_regression", saved["models"])
            self.assertEqual(
                saved["models"]["tfidf_logistic_regression"]["settings"][
                    "vectorizer_fitted_on"
                ],
                "training partition only",
            )


if __name__ == "__main__":
    unittest.main()
