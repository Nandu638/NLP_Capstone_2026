import csv
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from review_analytics.issues import (
    analyze_rows,
    match_themes,
    run_issue_analysis,
)


def row(app, text):
    return {"app_name": app, "review_text": text}


class ThemeMatchingTests(unittest.TestCase):
    def test_matches_expected_theme(self):
        self.assertEqual(
            match_themes("My delivery was delayed"),
            ("delivery_fulfilment",),
        )

    def test_one_review_can_match_overlapping_themes(self):
        matches = match_themes(
            "Payment was taken but refund for canceled order is missing"
        )
        self.assertIn("payment_issues", matches)
        self.assertIn("refunds_cancellations", matches)

    def test_empty_or_missing_text_has_no_candidate_matches(self):
        self.assertEqual(match_themes(""), ())
        self.assertEqual(match_themes(None), ())


class AnalysisTests(unittest.TestCase):
    def test_counts_and_percentages_use_review_denominators_with_overlap(self):
        summary = analyze_rows(
            [
                row("Amazon Shopping", "delivery delayed and payment failed"),
                row("Amazon Shopping", "delivery was good"),
                row("Flipkart", "product quality is poor"),
            ]
        )
        totals = {item["theme"]: item for item in summary["themes"]}
        by_app = {
            (item["app_name"], item["theme"]): item
            for item in summary["themes_by_app"]
        }

        self.assertEqual(summary["total_reviews"], 3)
        self.assertEqual(totals["delivery_fulfilment"]["keyword_candidate_reviews"], 2)
        self.assertEqual(totals["payment_issues"]["keyword_candidate_reviews"], 1)
        self.assertEqual(totals["product_quality"]["keyword_candidate_reviews"], 1)
        self.assertEqual(totals["delivery_fulfilment"]["dataset_review_denominator"], 3)
        self.assertEqual(totals["delivery_fulfilment"]["percent_of_all_reviews"], 66.67)
        self.assertEqual(
            by_app[("Amazon Shopping", "delivery_fulfilment")][
                "app_review_denominator"
            ],
            2,
        )
        self.assertEqual(
            by_app[("Amazon Shopping", "delivery_fulfilment")][
                "percent_of_app_reviews"
            ],
            100.0,
        )
        self.assertGreater(
            sum(item["percent_of_all_reviews"] for item in totals.values()),
            100,
        )

    def test_empty_text_stays_in_denominator_and_is_counted(self):
        summary = analyze_rows(
            [row("App", ""), row("App", "refund pending")]
        )
        refunds = next(item for item in summary["themes"] if item["theme"] == "refunds_cancellations")
        self.assertEqual(summary["total_reviews"], 2)
        self.assertEqual(summary["blank_review_text"], 1)
        self.assertEqual(refunds["keyword_candidate_reviews"], 1)
        self.assertEqual(refunds["dataset_review_denominator"], 2)
        self.assertEqual(refunds["percent_of_all_reviews"], 50.0)

    def test_missing_app_is_counted_explicitly(self):
        summary = analyze_rows([row("", "delivery")])
        self.assertEqual(summary["app_counts"]["<MISSING>"], 1)
        self.assertTrue(
            any(item["app_name"] == "<MISSING>" for item in summary["themes_by_app"])
        )


class OutputTests(unittest.TestCase):
    def test_generates_tables_figures_and_redacted_validation_sample(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.csv"
            tables_dir = root / "tables"
            figures_dir = root / "figures"
            with input_path.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=["app_name", "review_text", "review_id"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "app_name": "Amazon Shopping",
                        "review_text": "delivery delay contact me at name@example.com",
                        "review_id": "not exported",
                    }
                )
                writer.writerow(
                    {
                        "app_name": "Flipkart",
                        "review_text": "payment failed, refund pending",
                        "review_id": "not exported",
                    }
                )

            summary = run_issue_analysis(input_path, tables_dir, figures_dir)

            self.assertEqual(summary["total_reviews"], 2)
            self.assertEqual(len(summary["table_paths"]), 3)
            self.assertEqual(len(summary["figure_paths"]), 2)
            for path in summary["table_paths"] + summary["figure_paths"]:
                self.assertTrue(Path(path).is_file())
                self.assertGreater(Path(path).stat().st_size, 0)

            with (tables_dir / "issue_review_sample.csv").open(
                encoding="utf-8", newline=""
            ) as file:
                sample_rows = list(csv.DictReader(file))
            self.assertTrue(sample_rows)
            sample_text = " ".join(
                sample["review_text_redacted"] for sample in sample_rows
            )
            self.assertNotIn("name@example.com", sample_text)
            self.assertIn("[redacted email]", sample_text)
            self.assertTrue(
                all(
                    sample["validation_status"]
                    == "candidate; human validation pending"
                    for sample in sample_rows
                )
            )
            self.assertNotIn("review_id", sample_rows[0])

    def test_refuses_to_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.csv"
            input_path.write_text("app_name,review_text\nApp,delivery\n", encoding="utf-8")
            tables_dir = root / "tables"
            figures_dir = root / "figures"
            tables_dir.mkdir()
            existing = tables_dir / "issue_theme_counts.csv"
            existing.write_text("preserve", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                run_issue_analysis(input_path, tables_dir, figures_dir)

            self.assertEqual(existing.read_text(encoding="utf-8"), "preserve")


if __name__ == "__main__":
    unittest.main()
