# Exploratory Data Analysis Report

## Scope and method

This descriptive EDA used `data/processed/google_play_reviews_cleaned.csv`
as its input. It read the data without changing either that file or
`data/raw/google_play_reviews_processed.csv`.

The module uses the Python standard library for CSV reading and summary
calculations, plus the already available `matplotlib` dependency for figures.
The audit before analysis confirmed 5,840 rows, 15 fields, and 15 fields on
every row. No missing fields or malformed row widths were observed.

- App, rating, and sentiment distributions are record counts.
- Per-app percentages use the total observed records for that app as the
  denominator.
- Review length is measured from `clean_text_new` as Python character count
  and whitespace-separated token count.
- Length summaries include count, mean, median, 95th percentile (linear
  interpolation), minimum, and maximum.
- Blank categorical values are represented explicitly as `<MISSING>` and
  unexpected values are retained as their observed categories. No records are
  silently dropped. The actual input contained no missing app, rating,
  sentiment, or `clean_text_new` values and no unexpected app, rating, or
  sentiment categories.

## Record counts

| App | Records |
|---|---:|
| Amazon Shopping | 1,964 |
| Flipkart | 1,900 |
| Myntra | 1,976 |
| **Total** | **5,840** |

The app counts sum to the input row count. All 5,840 records are represented in
the rating, sentiment, and text-length summaries.

## Rating distribution

| Rating | Records |
|---:|---:|
| 1 | 1,562 |
| 2 | 249 |
| 3 | 279 |
| 4 | 438 |
| 5 | 3,312 |
| **Total** | **5,840** |

### Rating mix by app

Percentages use each app's own row count.

| App | Rating 1 | Rating 2 | Rating 3 | Rating 4 | Rating 5 |
|---|---:|---:|---:|---:|---:|
| Amazon Shopping (n=1,964) | 1,034 (52.65%) | 174 (8.86%) | 135 (6.87%) | 77 (3.92%) | 544 (27.70%) |
| Flipkart (n=1,900) | 269 (14.16%) | 56 (2.95%) | 116 (6.11%) | 206 (10.84%) | 1,253 (65.95%) |
| Myntra (n=1,976) | 259 (13.11%) | 19 (0.96%) | 28 (1.42%) | 155 (7.84%) | 1,515 (76.67%) |

## Observed sentiment-label distribution

| Sentiment label | Records |
|---|---:|
| negative | 1,811 |
| neutral | 279 |
| positive | 3,750 |
| **Total** | **5,840** |

### Sentiment-label mix by app

Percentages use each app's own row count. These are distributions of the
observed labels, not independently verified measures of review sentiment.

| App | Negative | Neutral | Positive |
|---|---:|---:|---:|
| Amazon Shopping (n=1,964) | 1,208 (61.51%) | 135 (6.87%) | 621 (31.62%) |
| Flipkart (n=1,900) | 325 (17.11%) | 116 (6.11%) | 1,459 (76.79%) |
| Myntra (n=1,976) | 278 (14.07%) | 28 (1.42%) | 1,670 (84.51%) |

## Rating and label consistency

The complete rating-versus-sentiment counts were:

| Rating | Negative | Neutral | Positive | Row total |
|---:|---:|---:|---:|---:|
| 1 | 1,562 | 0 | 0 | 1,562 |
| 2 | 249 | 0 | 0 | 249 |
| 3 | 0 | 279 | 0 | 279 |
| 4 | 0 | 0 | 438 | 438 |
| 5 | 0 | 0 | 3,312 | 3,312 |
| **Total** | **1,811** | **279** | **3,750** | **5,840** |

All 5,840 records align with the tested rating mapping (ratings 1–2
`negative`, 3 `neutral`, 4–5 `positive`): **5,840 matched, 0 conflicts, and
0 unassessable**. The prior sentiment-label audit and project documentation
do not establish the labels' historical origin. Their provenance remains
unverified; this perfect alignment does not prove that labels were generated
from ratings or establish them as independent sentiment ground truth.

## Review-text length

Length is calculated from `clean_text_new`, not the older `clean_text` field.

| Scope | Measure | Count | Mean | Median | P95 | Min | Max |
|---|---|---:|---:|---:|---:|---:|---:|
| All apps | Characters | 5,840 | 82.77 | 22 | 425.05 | 2 | 500 |
| All apps | Whitespace-separated tokens | 5,840 | 15.05 | 4 | 75 | 1 | 106 |
| Amazon Shopping | Characters | 1,964 | 155.63 | 105 | 480 | 2 | 500 |
| Amazon Shopping | Tokens | 1,964 | 28.58 | 19 | 87 | 1 | 106 |
| Flipkart | Characters | 1,900 | 32.08 | 8 | 165.10 | 2 | 500 |
| Flipkart | Tokens | 1,900 | 5.86 | 2 | 30.05 | 1 | 102 |
| Myntra | Characters | 1,976 | 59.09 | 19 | 329 | 2 | 500 |
| Myntra | Tokens | 1,976 | 10.45 | 3 | 56 | 1 | 100 |

## Figures

The pipeline creates the following labeled figures:

- [Rating distribution](outputs/figures/rating_distribution.png)
- [Sentiment-label distribution](outputs/figures/sentiment_distribution.png)
- [Rating and sentiment comparison by app](outputs/figures/app_comparison.png)
- [Review character-length comparison by app](outputs/figures/review_length_by_app.png)

The length comparison is a box plot with outlier markers hidden for
readability; the full minimum and maximum values remain in the summary table.

## Summary tables

The pipeline writes machine-readable CSV tables under `outputs/tables/`:

- `app_counts.csv`
- `rating_counts.csv`
- `app_rating_counts.csv` (counts and within-app percentages)
- `rating_sentiment_counts.csv`
- `sentiment_counts.csv`
- `app_sentiment_counts.csv` (counts and within-app percentages)
- `review_length_summary.csv`

## Limitations

This stage is descriptive only. The app-specific distributions show observed
differences in this dataset and do not establish causes, app-wide customer
experience, or generalizable population differences. Sentiment labels are
rating-aligned, with original provenance unverified. Review lengths describe
the `clean_text_new` representation produced by the documented conservative
cleaning rules; character and token counts are not measures of review quality.
No frequent-word analysis, issue classification, topic modeling, sentiment
modeling, training, or business recommendations were performed.

## Tests and reproducibility

The focused EDA tests use small synthetic records and cover count
calculations, app/rating/sentiment summaries, character and token lengths,
explicit missing/unexpected values, missing columns, and malformed rows.
Final test run: **12 tests passed, 0 failures** (includes the existing focused
cleaning tests).

With the existing Python 3.14.7 environment and already-installed
`matplotlib`, run from the project root in PowerShell:

```powershell
& 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe' -m unittest discover -s tests -v
& 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe' 'src\review_analytics\eda.py'
```

The EDA command reads the cleaned CSV and regenerates the figures and tables.
It prints the computed summary as JSON. No packages were installed.
