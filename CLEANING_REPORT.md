# Data Cleaning Report

## Scope and source

This stage created `data/processed/google_play_reviews_cleaned.csv` from the
immutable source `data/raw/google_play_reviews_processed.csv`. The approved
validation reports describe **5,840 records** and 14 source columns, including
`review_text`, `rating`, `sentiment`, and the existing `clean_text`.

The cleaning pipeline reads `review_text` as its only input for the new text
field. It retains every input column and row, including the existing
`clean_text`, and appends `clean_text_new`. It does not modify the source CSV.

## Cleaning rules

For each `review_text` value, `clean_text_new` is produced by:

1. Unicode canonical composition using NFC.
2. Lowercasing.
3. Standardizing whitespace by splitting on whitespace and joining tokens
   with one ordinary space (which also trims leading/trailing whitespace).

Missing (`None`) or whitespace-only text produces an empty string. No URL,
punctuation, number, negation, or frequent word is deliberately removed.
URLs, punctuation, and numbers are retained by the implementation.

The `rating` and `sentiment` fields, along with all other original columns,
are copied unchanged. The sentiment audit found that all 5,840 labels align
with the tested rating mapping (ratings 1–2 negative, 3 neutral, 4–5 positive);
the original label provenance remains unverified. This cleaning stage does
not relabel or interpret them.

## Before/after checks

| Check | Observed result |
|---|---:|
| Source records | 5,840 |
| Output records | 5,840 |
| Rows excluded | 0 |
| Source columns | 14 |
| Output columns | 15 |
| Original columns/values preserved exactly | Yes |
| `clean_text_new` values matching the documented rule | 5,840 of 5,840 |
| Blank/whitespace-only source `review_text` | 0 |
| Blank/whitespace-only output `clean_text_new` | 0 |
| Rows where `clean_text_new` differs from `review_text` | 2,379 |
| Rows affected by NFC normalization | 0 |
| Rows affected by lowercasing | 2,379 |
| Rows affected by whitespace standardization | 0 |

These are dataset-specific checks. The operation counts are checks against
each individual normalization step and are not intended to characterize the
older `clean_text` column.

## Tests

The focused test suite passed: **8 tests, 0 failures**. It covers missing and
blank values, whitespace, lowercase conversion, NFC handling, negation and
punctuation/number/URL retention, preservation of original text and label
columns, output overwrite protection, and malformed-row failure without
creating a partial output.

The pipeline aborts on malformed row widths; it does not silently discard
records. It also refuses to overwrite an existing output file.

## Limitations

- Lowercasing removes case distinctions. NFC performs canonical Unicode
  normalization but does not transliterate or otherwise simplify text.
- Standardized whitespace does not remove punctuation or tokens.
- The checks establish that `clean_text_new` follows the stated rule and
  original CSV values are preserved. They do not establish that this is the
  best text representation for a later modeling task.
- The existing `sentiment` values remain rating-aligned with unknown
  provenance; they should not be treated as independently verified sentiment
  ground truth based on this cleaning step.

## Reproducibility

No third-party dependencies are required. Using the existing Python 3.14.7
environment, run these commands from the project root in PowerShell:

```powershell
& 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe' -m unittest discover -s tests -v
& 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe' 'src\review_analytics\cleaning.py'
```

The cleaning command uses the default raw input and processed output paths
shown above. It prints a JSON summary and will stop rather than overwrite an
existing output.
