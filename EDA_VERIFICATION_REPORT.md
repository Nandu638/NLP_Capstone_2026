# EDA Verification Report

## Scope

This was a read-only verification of the EDA outputs and source datasets. No
CSV, figure, analysis code, or existing report was modified. The only file
created for this check is this report.

## EDA output files

All four figures and all seven summary tables listed in `EDA_REPORT.md` exist
and have nonzero size.

| Output | Bytes | Status |
|---|---:|---|
| `outputs/figures/rating_distribution.png` | 30,831 | Present, nonempty |
| `outputs/figures/sentiment_distribution.png` | 34,470 | Present, nonempty |
| `outputs/figures/app_comparison.png` | 95,946 | Present, nonempty |
| `outputs/figures/review_length_by_app.png` | 42,763 | Present, nonempty |
| `outputs/tables/app_counts.csv` | 69 | Present, nonempty |
| `outputs/tables/rating_counts.csv` | 52 | Present, nonempty |
| `outputs/tables/app_rating_counts.csv` | 371 | Present, nonempty |
| `outputs/tables/rating_sentiment_counts.csv` | 232 | Present, nonempty |
| `outputs/tables/sentiment_counts.csv` | 63 | Present, nonempty |
| `outputs/tables/app_sentiment_counts.csv` | 307 | Present, nonempty |
| `outputs/tables/review_length_summary.csv` | 407 | Present, nonempty |

## Independent distribution checks

Independently reading `data/processed/google_play_reviews_cleaned.csv`
produced **5,840 rows**. The raw source also has **5,840 rows**. Recomputed
counts match `EDA_REPORT.md`:

- **App:** Amazon Shopping 1,964; Flipkart 1,900; Myntra 1,976.
- **Rating:** 1: 1,562; 2: 249; 3: 279; 4: 438; 5: 3,312.
- **Sentiment:** negative 1,811; neutral 279; positive 3,750.
- **Rating/sentiment cells:** 1/negative 1,562; 2/negative 249;
  3/neutral 279; 4/positive 438; 5/positive 3,312. Other cells are zero.
- **Blank `clean_text_new`:** 0.

App, rating, sentiment, and rating/sentiment table totals each sum to 5,840.
No discrepancy from the report was found.

## Investigation of the 500-character maximum

Independent checks found:

- Maximum raw `review_text` length: **500 characters**.
- Raw `review_text` records exactly 500 characters: **23**.
- Raw `review_text` records longer than 500 characters: **0**.
- Raw `review_text` records exactly 499 characters: **19**.
- Records with `clean_text_new` length exactly 500, by app:

| App | `clean_text_new` length = 500 | Corresponding original `review_text` length = 500 |
|---|---:|---:|
| Amazon Shopping | 11 | 11 |
| Flipkart | 5 | 5 |
| Myntra | 7 | 7 |
| **Total** | **23** | **23** |

The raw `review_text` values match the corresponding cleaned CSV
`review_text` values in all 5,840 row pairs. Thus, the 500-character values
already occur in the raw file; this EDA did not create that limit. For these
23 records, 14 end with an alphanumeric character and 9 end with punctuation
or another symbol. The older `clean_text` field for these same records ranges
from 317 to 490 characters; it is not the field used for the EDA length
maximum.

The inspected `EDA_REPORT.md`, `CLEANING_REPORT.md`,
`DATA_VALIDATION_REPORT.md`, `TEXT_READINESS_AUDIT.md`, and
`SENTIMENT_LABEL_AUDIT.md` do not document a 500-character source limit or
establish truncation. The cleaning module documents only NFC normalization,
lowercasing, and whitespace standardization; it does not truncate text.
`TEXT_READINESS_AUDIT.md` notes possible prefix differences in the older
`clean_text` field but does not identify their cause or connect them to a
500-character upstream limit.

**Conclusion:** A 500-character ceiling is an observed pattern: the maximum
raw review length is 500 and there are 23 values at that length, with none
longer. This is consistent with a possible upstream limit, but the available
data and project documentation do not establish whether these reviews were
truncated, naturally ended at that length, or were subject to some other
source-side behavior. This report does **not** claim that truncation occurred.

## File integrity fingerprints

SHA-256 hashes were calculated by streaming each file read-only:

| File | Bytes | SHA-256 |
|---|---:|---|
| `data/raw/google_play_reviews_processed.csv` | 1,866,449 | `0a213d2af8514bece200d3a40a3046c0ad4e955ece32a5afe370a4cc7986ab98` |
| `data/processed/google_play_reviews_cleaned.csv` | 2,359,578 | `b932e2589ec49fbcbe54532b93cfadd23f4f4e549b3bb9af91cdc911be3e63b1` |

The file sizes and modification times match the inventory recorded after the
EDA pipeline ran: raw source **1,866,449 bytes**, modified
**2026-10-15 11:31:27**; cleaned input **2,359,578 bytes**, modified
**2026-10-22 09:18:06**. The current hashes are fingerprints for future
comparison; pre-EDA hashes were not recorded, so a byte-for-byte historical
hash comparison is unavailable. The matching recorded sizes/timestamps and
the EDA pipeline's read-only input behavior provide no indication that either
CSV changed during EDA.

## Commands used

From the project root in PowerShell, the output-file check and current hashes
were obtained with:

```powershell
$expected = @(
  'outputs\figures\rating_distribution.png',
  'outputs\figures\sentiment_distribution.png',
  'outputs\figures\app_comparison.png',
  'outputs\figures\review_length_by_app.png',
  'outputs\tables\app_counts.csv',
  'outputs\tables\rating_counts.csv',
  'outputs\tables\app_rating_counts.csv',
  'outputs\tables\rating_sentiment_counts.csv',
  'outputs\tables\sentiment_counts.csv',
  'outputs\tables\app_sentiment_counts.csv',
  'outputs\tables\review_length_summary.csv'
)
foreach ($relative in $expected) {
  $item = Get-Item -LiteralPath $relative
  [PSCustomObject]@{ Path = $relative; Bytes = $item.Length; Nonempty = ($item.Length -gt 0) }
}
Get-FileHash -LiteralPath 'data\raw\google_play_reviews_processed.csv' -Algorithm SHA256
Get-FileHash -LiteralPath 'data\processed\google_play_reviews_cleaned.csv' -Algorithm SHA256
```

Independent counts, text lengths, and paired raw/cleaned review text were
computed using the existing Python 3.14.7 interpreter and standard library:

```powershell
@'
import csv
from collections import Counter
from pathlib import Path

raw_path = Path("data/raw/google_play_reviews_processed.csv")
clean_path = Path("data/processed/google_play_reviews_cleaned.csv")
apps, ratings, sentiments, cells = Counter(), Counter(), Counter(), Counter()
cap_by_app, raw_cap_by_app, raw_lengths = Counter(), Counter(), Counter()
pair_mismatches = raw_rows = cleaned_rows = 0
with raw_path.open(encoding="utf-8-sig", newline="") as raw_file, \
     clean_path.open(encoding="utf-8", newline="") as clean_file:
    raw_reader = csv.DictReader(raw_file, strict=True)
    clean_reader = csv.DictReader(clean_file, strict=True)
    for raw, clean in zip(raw_reader, clean_reader):
        raw_rows += 1
        cleaned_rows += 1
        pair_mismatches += raw["review_text"] != clean["review_text"]
        raw_lengths[len(raw["review_text"])] += 1
        app, rating, sentiment = (
            clean["app_name"], clean["rating"], clean["sentiment"]
        )
        apps[app] += 1
        ratings[rating] += 1
        sentiments[sentiment] += 1
        cells[(rating, sentiment)] += 1
        if len(clean["clean_text_new"]) == 500:
            cap_by_app[app] += 1
            raw_cap_by_app[app] += int(len(raw["review_text"]) == 500)
print("rows:", raw_rows, cleaned_rows)
print("apps:", dict(apps))
print("ratings:", dict(ratings))
print("sentiments:", dict(sentiments))
print("rating/sentiment:", dict(cells))
print("raw lengths:", max(raw_lengths), raw_lengths[499], raw_lengths[500])
print("raw lengths > 500:", sum(
    count for length, count in raw_lengths.items() if length > 500
))
print("500-character records by app:", dict(cap_by_app))
print("corresponding original text length 500:", dict(raw_cap_by_app))
print("review_text mismatches:", pair_mismatches)
'@ | & 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe' -
```
