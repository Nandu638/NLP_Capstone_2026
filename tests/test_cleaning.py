import csv
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from review_analytics.cleaning import clean_csv, clean_text


class CleanTextTests(unittest.TestCase):
    def test_missing_and_blank_text_become_empty(self):
        self.assertEqual(clean_text(None), "")
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text(" \t\r\n "), "")

    def test_standardizes_whitespace(self):
        self.assertEqual(clean_text("  One\t two\n three  "), "one two three")

    def test_lowercases_text(self):
        self.assertEqual(clean_text("Great APP"), "great app")

    def test_normalizes_unicode_to_nfc(self):
        self.assertEqual(clean_text("Cafe\u0301"), "café")

    def test_preserves_negations_punctuation_numbers_and_urls(self):
        text = "NOT no never isn't; 24/7! https://example.com"
        self.assertEqual(
            clean_text(text),
            "not no never isn't; 24/7! https://example.com",
        )


class CleanCsvTests(unittest.TestCase):
    def test_preserves_original_text_labels_columns_and_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.csv"
            output = root / "output.csv"
            original_rows = [
                {
                    "review_text": "  NOT good\t!",
                    "rating": "1",
                    "sentiment": "negative",
                    "clean_text": "different prior value",
                    "app_name": "Example",
                },
                {
                    "review_text": "Cafe\u0301",
                    "rating": "5",
                    "sentiment": "positive",
                    "clean_text": "",
                    "app_name": "Example",
                },
            ]
            original_columns = list(original_rows[0])
            with source.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=original_columns)
                writer.writeheader()
                writer.writerows(original_rows)
            source_before = source.read_bytes()

            stats = clean_csv(source, output)

            with output.open("r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                output_rows = list(reader)
                output_columns = reader.fieldnames

            self.assertEqual(source.read_bytes(), source_before)
            self.assertEqual(output_columns, original_columns + ["clean_text_new"])
            self.assertEqual(len(output_rows), len(original_rows))
            for original, result in zip(original_rows, output_rows):
                for column in original_columns:
                    self.assertEqual(result[column], original[column])
            self.assertEqual(
                [row["clean_text_new"] for row in output_rows],
                ["not good !", "café"],
            )
            self.assertEqual(stats["rows_written"], 2)
            self.assertEqual(stats["blank_review_text"], 0)

    def test_refuses_to_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.csv"
            output = root / "output.csv"
            source.write_text("review_text\nsample\n", encoding="utf-8")
            output.write_text("keep me", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                clean_csv(source, output)

            self.assertEqual(output.read_text(encoding="utf-8"), "keep me")

    def test_malformed_row_fails_without_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.csv"
            output = root / "output.csv"
            source.write_text("review_text,rating\ntext,1,extra\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "more fields"):
                clean_csv(source, output)

            self.assertFalse(output.exists())
            self.assertEqual(list(root.glob(".output.csv.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
