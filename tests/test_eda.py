import sys
import unittest


PROJECT_ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from review_analytics.eda import analyze_rows


def review(app, rating, sentiment, text):
    return {
        "app_name": app,
        "rating": rating,
        "sentiment": sentiment,
        "clean_text_new": text,
    }


class AnalyzeRowsTests(unittest.TestCase):
    def test_counts_by_app_rating_sentiment_and_lengths(self):
        rows = [
            review("Amazon Shopping", "1", "negative", "not great"),
            review("Amazon Shopping", "5", "positive", "very good"),
            review("Flipkart", "3", "neutral", "okay"),
        ]

        summary = analyze_rows(rows)

        self.assertEqual(summary["row_count"], 3)
        self.assertEqual(summary["app_counts"]["Amazon Shopping"], 2)
        self.assertEqual(summary["app_counts"]["Flipkart"], 1)
        self.assertEqual(summary["rating_counts"], {"1": 1, "3": 1, "5": 1})
        self.assertEqual(
            summary["sentiment_counts"],
            {"negative": 1, "positive": 1, "neutral": 1},
        )
        self.assertEqual(summary["app_rating_counts"]["Amazon Shopping"]["5"], 1)
        self.assertEqual(summary["app_sentiment_counts"]["Flipkart"]["neutral"], 1)
        self.assertEqual(summary["rating_sentiment_counts"]["1"]["negative"], 1)
        self.assertEqual(summary["rating_sentiment_counts"]["5"]["positive"], 1)
        self.assertEqual(summary["lengths"]["characters"]["count"], 3)
        self.assertEqual(summary["lengths"]["characters"]["mean"], 7.33)
        self.assertEqual(summary["lengths"]["tokens"]["min"], 1)
        self.assertEqual(summary["lengths"]["tokens"]["max"], 2)
        self.assertEqual(summary["lengths_by_app"]["Amazon Shopping"]["count"], 2)
        self.assertEqual(summary["token_lengths_by_app"]["Flipkart"]["mean"], 1)
        self.assertEqual(
            summary["rating_sentiment_alignment"],
            {"matched": 3, "conflicts": 0, "unassessable": 0},
        )

    def test_missing_and_unexpected_categories_are_counted(self):
        rows = [
            review("", "", "", ""),
            review("New App", "6", "mixed", "Some text"),
        ]

        summary = analyze_rows(rows)

        self.assertEqual(summary["row_count"], 2)
        self.assertEqual(summary["app_counts"]["<MISSING>"], 1)
        self.assertEqual(summary["rating_counts"]["<MISSING>"], 1)
        self.assertEqual(summary["rating_counts"]["6"], 1)
        self.assertEqual(summary["sentiment_counts"]["<MISSING>"], 1)
        self.assertEqual(summary["sentiment_counts"]["mixed"], 1)
        self.assertEqual(
            summary["missing_counts"],
            {
                "app_name": 1,
                "rating": 1,
                "sentiment": 1,
                "clean_text_new": 1,
            },
        )
        self.assertEqual(summary["lengths"]["characters"]["count"], 2)
        self.assertEqual(
            summary["rating_sentiment_alignment"],
            {"matched": 0, "conflicts": 0, "unassessable": 2},
        )

    def test_raises_on_missing_required_column(self):
        with self.assertRaisesRegex(ValueError, "missing required columns"):
            analyze_rows([{"app_name": "App"}])

    def test_raises_on_short_row_instead_of_dropping_it(self):
        row = review("App", "1", "negative", "text")
        row["rating"] = None
        with self.assertRaisesRegex(ValueError, "fewer fields"):
            analyze_rows([row])


if __name__ == "__main__":
    unittest.main()
