# Dataset Validation Report

**Dataset inspected:** `data/raw/google_play_reviews_processed.csv`  
**Method:** Read-only Python 3.14.7 script using the standard library (`csv`,
`collections`, and related built-ins); no packages installed.  
**Missing-value definition:** Empty or whitespace-only cells. Text tokens such
as `"NA"` or `"null"` were not treated as missing.  
**Type inference:** Lexical inspection of all nonblank values; this is not a
schema declaration.

## Observed facts

- The file was read completely using UTF-8 with BOM support (`utf-8-sig`).
- There were **5,840 data records** and **14 columns**.
- All 5,840 records had the expected 14 fields. No malformed-width rows or
  CSV parsing errors were encountered.
- No UTF-8 decoding or other encoding issue was encountered.
- There were **0 exact duplicate data rows**.
- `review_text` exists and has **0 empty records** under the missing-value
  definition above.
- Column names, inferred types, and missing-value counts:

| Column | Inferred type | Missing values |
|---|---|---:|
| `app_name` | string | 0 |
| `package_id` | string | 0 |
| `review_id` | string | 0 |
| `review_text` | string | 0 |
| `rating` | integer | 0 |
| `thumbs_up_count` | integer | 0 |
| `review_date` | string | 0 |
| `review_version` | mixed (decimal, text) | 763 |
| `app_version` | mixed (decimal, text) | 0 |
| `collected_at_utc` | string | 0 |
| `country` | string | 0 |
| `language` | string | 0 |
| `sentiment` | string | 0 |
| `clean_text` | string | 0 |

### Observed categorical values and counts

| Column | Value | Count |
|---|---|---:|
| `app_name` | Amazon Shopping | 1,964 |
| `app_name` | Flipkart | 1,900 |
| `app_name` | Myntra | 1,976 |
| `package_id` | `com.amazon.mShop.android.shopping` | 1,964 |
| `package_id` | `com.flipkart.android` | 1,900 |
| `package_id` | `com.myntra.android` | 1,976 |
| `sentiment` | negative | 1,811 |
| `sentiment` | neutral | 279 |
| `sentiment` | positive | 3,750 |
| `country` | `in` | 5,840 |
| `language` | `en` | 5,840 |
| `collected_at_utc` | `2026-10-15T06:01:17.635516+00:00` | 5,840 |

### Rating observations

The `rating` column was inferred as integer. All **5,840** values were
numeric. The observed minimum is **1**, the observed maximum is **5**, and
the distinct observed values are **1, 2, 3, 4, 5**. These are observed values,
not a confirmed allowed range: no authoritative rating specification was
provided for comparison.

## Potential issues and recommendations

- `review_version` has 763 empty values and a mixed inferred type among
  nonempty values. Preserve these facts during later preparation; decide how
  to handle the field only after reviewing the data requirements.
- The observed `country`, `language`, and collection timestamp each have one
  value across all records. This may reflect the dataset's collection scope;
  confirm the intended scope before drawing conclusions beyond it.
- `sentiment` labels are present, but their origin and labeling method have
  not been established by this validation. Confirm their provenance before
  using them as classification targets.
- Confirm the rating's allowed values against authoritative dataset
  documentation before calling its range valid or invalid.
- Missing-value counts cover blank cells only. If the source uses literal
  sentinel strings for missingness, those require an explicit, documented
  decision.

No records were repaired, cleaned, relabeled, or dropped. No EDA, topic
modeling, sentiment classification, or other analysis was performed.

## Command used

Run from the project root in PowerShell:

```powershell
& 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe' '_validate_dataset_temp.py'
```

The temporary validation script used for this read-only inspection was removed
after it ran. The report is the only file created for this stage.
