# Customer Issue Analysis Report

## Scope and input

This stage performed keyword-based candidate detection only. It did not clean or
modify data, classify sentiment, train a model, perform topic modelling, validate
themes manually, infer causes, or make final business recommendations.

Input: `data/processed/google_play_reviews_cleaned.csv`. The analysis used the
original `review_text` and `app_name` fields. The file contained 5,840 readable
records across Amazon Shopping (1,964), Flipkart (1,900), and Myntra (1,976).
No blank review text was observed. All records were retained in the denominator;
no rows were dropped. The raw and cleaned dataset SHA-256 hashes were unchanged
by the run.

Sentiment was not used to detect or count themes. Project evidence indicates the
existing sentiment labels align with ratings, but their historical provenance
remains unverified.

## Method

The reproducible detector in `src/review_analytics/issues.py` searches
case-insensitively for the following whole-word or phrase terms in `review_text`:

| Candidate theme | Configured terms |
|---|---|
| Delivery and fulfilment | delivery, deliver, delivered, delivering, courier, shipment, shipping, shipped, parcel, late delivery, delivery delay, delayed, delay, not received, delivery boy, delivery partner, fulfilment, fulfillment |
| Customer support | customer service, customer care, customer support, support team, helpline, help line, call center, call centre, customer executive, support executive, customer agent |
| Refunds and cancellations | refund, refunded, refunds, refunding, cancel, canceled, cancelled, cancellation, cancellations, return, returned, returning, replacement, replace |
| App functionality | crash, crashes, crashing, bug, bugs, error, errors, not working, does not work, doesn't work, won't open, not opening, login, log in, loading, stuck, freeze, frozen, glitch, glitches, hangs, hanging |
| Product quality | poor quality, bad quality, quality issue(s), product quality, material quality, damaged, defective, broken item, broken product, fake product, counterfeit, wrong product, wrong item, size issue, size problem |
| Payment issues | payment, paid, transaction, UPI, credit card, debit card, card declined, wallet, charged, double charged, billing, cash on delivery |

Each review is counted once per matching theme, while one review may match
multiple themes. Therefore theme counts and percentages overlap and percentages
may sum to more than 100%. Terms are not sentiment-aware: a match may occur in a
positive, neutral, or negative context and is not by itself a confirmed
complaint.

Overall percentage denominator: all 5,840 input reviews. App-level percentage
denominator: all reviews for that app. Blank text, if encountered, would remain
in the denominator and match no themes; missing app names are explicitly grouped
as `<MISSING>`.

The manual-validation sample is reproducible: select the first safe matching
record in input order for each app/theme cell, then deduplicate repeated records.
The sample includes the source row number, app, detected candidate themes, and
redacted text; it excludes review IDs and package IDs. Common emails, URLs,
handles, phone-like numbers, order/reference strings, and explicit personal
detail introductions are redacted. The sample is for subsequent human review;
no examples have yet been manually validated.

## Observed results

### Overall candidate counts

| Candidate theme | Reviews containing configured terms | Denominator | Percent |
|---|---:|---:|---:|
| Delivery and fulfilment | 638 | 5,840 | 10.92% |
| Customer support | 291 | 5,840 | 4.98% |
| Refunds and cancellations | 335 | 5,840 | 5.74% |
| App functionality | 147 | 5,840 | 2.52% |
| Product quality | 52 | 5,840 | 0.89% |
| Payment issues | 115 | 5,840 | 1.97% |

### App comparison

Counts and percentages use each app's full record count as the denominator.
These are keyword-detection rates, not validated complaint rates.

| Candidate theme | Amazon Shopping (n=1,964) | Flipkart (n=1,900) | Myntra (n=1,976) |
|---|---:|---:|---:|
| Delivery and fulfilment | 327 (16.65%) | 124 (6.53%) | 187 (9.46%) |
| Customer support | 137 (6.98%) | 48 (2.53%) | 106 (5.36%) |
| Refunds and cancellations | 166 (8.45%) | 52 (2.74%) | 117 (5.92%) |
| App functionality | 126 (6.42%) | 9 (0.47%) | 12 (0.61%) |
| Product quality | 19 (0.97%) | 10 (0.53%) | 23 (1.16%) |
| Payment issues | 75 (3.82%) | 21 (1.11%) | 19 (0.96%) |

The deterministic validation sample contains 13 unique records and covers all
six candidate themes. It remains pending human review. No sample text is
reproduced in this report.

## Outputs

Summary tables:

- `outputs/tables/issue_theme_counts.csv` — overall counts and percentages.
- `outputs/tables/issue_theme_by_app.csv` — app-level counts and percentages.
- `outputs/tables/issue_review_sample.csv` — redacted sample for manual review.

Figures:

- `outputs/figures/issue_theme_prevalence.png` — overall candidate counts and rates.
- `outputs/figures/issue_theme_by_app.png` — app-level candidate rates.

All five outputs were verified to exist and be nonempty.

## Limitations

- Keyword matches are candidate detections, not manually validated themes.
- Keywords can match non-complaint or ambiguous contexts; sarcasm, paraphrases,
  spelling variants, and context are not resolved.
- Failure to detect a keyword does not establish that an issue is absent.
- App-level differences are descriptive associations only; they do not establish
  causes or explain customer experience.
- The sample is deterministic and bounded, not a statistically representative
  validation sample. Automated redaction targets common identifiers and cannot
  guarantee detection of every identifying detail.
- Existing rating-aligned sentiment labels have unverified historical
  provenance and were not used as an independent sentiment measure here.

## Reproducibility

The analysis uses the existing Python environment and `matplotlib`; no packages
were installed. From the project root, run:

```powershell
$env:PYTHONPATH = 'src'
& 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe' -m review_analytics.issues
```

It refuses to overwrite any of its five output files. Focused and full test
commands:

```powershell
& 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe' -m unittest discover -s tests -p 'test_issues.py' -v
& 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe' -m unittest discover -s tests -v
```

Results for this run: all 8 focused issue-analysis tests passed, and all 24
project tests passed.
