# Text Readiness Audit

**Dataset:** `data/raw/google_play_reviews_processed.csv`  
**Method:** Read-only CSV inspection with the existing Python environment and standard library; source text is not printed to the console. Example text below was screened and redacted before inclusion.

## Rating-versus-sentiment cross-tabulation

Each cell gives the exact record count for that rating and sentiment.

| Rating | Row total | negative | neutral | positive |
|---:|---:|---:|---:|---:|
| 1 | 1,562 | 1,562 | 0 | 0 |
| 2 | 249 | 249 | 0 | 0 |
| 3 | 279 | 0 | 279 | 0 |
| 4 | 438 | 0 | 0 | 438 |
| 5 | 3,312 | 0 | 0 | 3,312 |
| **Total** | **5,840** | **1,811** | **279** | **3,750** |

## Representative differing text pairs

Ten differing records were selected in round-robin order across available app/sentiment groups. Text was screened for contact details, identifiers, address cues, personal-context terms, long text, digits, and title-cased proper nouns; examples that raised these flags were excluded. The remaining examples were redacted for emails, URLs, handles, and long numbers. Automated screening cannot guarantee detection of every possible identifying detail.

| Record | App | Sentiment | `review_text` (screened) | `clean_text` (screened) |
|---:|---|---|---|---|
| 2 | Amazon Shopping | negative | full of bug | full bug |
| 34 | Amazon Shopping | neutral | not available for android tablets | not available android tablets |
| 46 | Amazon Shopping | positive | good 👍 | good |
| 2021 | Flipkart | negative | Very bad app. | bad app |
| 2001 | Flipkart | neutral | good very | good |
| 1966 | Flipkart | positive | nice to see you tomorrow | nice see tomorrow |
| 3882 | Myntra | negative | very poor delivery network outside of kolkata | poor delivery network outside kolkata |
| 4016 | Myntra | neutral | quality of products good | quality products good |
| 3865 | Myntra | positive | very good product and options | good product options |
| 16 | Amazon Shopping | negative | wish list is now broken. instead of adding to your wish list, it creates a new, unique list and adds to that. | wish list now broken instead adding wish list creates new unique list adds |

Examples passing the text screen: **10** (requested: 10).

## Negation-word check

Case-insensitive whole-word checks were used for `not`, `no`, `never`, and the contraction suffix `n't`. Counts are shown as both total occurrences and records containing the form.

| Form | `review_text` occurrences | `review_text` records | `clean_text` occurrences | `clean_text` records |
|---|---:|---:|---:|---:|
| `not` | 694 | 545 | 694 | 545 |
| `no` | 417 | 337 | 417 | 337 |
| `never` | 163 | 140 | 163 | 140 |
| `n't` | 763 | 561 | 763 | 561 |

The row-presence overlap (among records containing each form in `review_text`) was:

- `not`: 545 records also contain it in `clean_text`.
- `no`: 337 records also contain it in `clean_text`.
- `never`: 140 records also contain it in `clean_text`.
- `n't`: 561 records also contain it in `clean_text`.

## Blank values and observed difference patterns

- Records inspected: **5,840**.
- Blank or whitespace-only `review_text`: **0**.
- Blank or whitespace-only `clean_text`: **0**.
- Exact string matches: **1,862**.
- Records where the fields differ exactly: **3,978**.

Each differing row was assigned to the first matching category below; categories are mutually exclusive for this summary:

| Observed comparison | Records |
|---|---:|
| whitespace-only difference | 0 |
| case and/or whitespace normalization | 263 |
| punctuation and/or spacing normalization | 413 |
| clean_text is a prefix (possible truncation) | 47 |
| review_text is a prefix (clean_text is longer) | 0 |
| ordered token removal | 3,160 |
| other / not classified by these checks | 95 |

These comparisons identify textual patterns only. A normalized form can also have token changes; a prefix may reflect an intentional transformation or truncation; and an unclassified difference may involve several operations. The observed counts do not establish the transformation's purpose or correctness.

## Label provenance

The inspected project documentation—`PROJECT_PLAN.md`, `README.md`, `DATA_VALIDATION_REPORT.md`, and `SENTIMENT_LABEL_AUDIT.md`—does not explain who or what originally assigned the sentiment labels or describe a labeling procedure. The sentiment audit reports perfect agreement with the tested rating mapping, but explicitly does not establish label origin. Provenance remains unknown.

## Limitations and recommendation

This was a read-only text-field readiness check, not cleaning, semantic review, or a determination that `clean_text` is better than `review_text`. Text-pair examples were screened conservatively, but automated screening cannot guarantee complete detection of personal information. The negation scan counts the specified spellings only; it does not evaluate context, scope, or semantic preservation. Pattern categories are descriptive heuristics, not evidence of the actual transformation pipeline.

Before cleaning, preserve `review_text` as the source field and do not assume `clean_text` is suitable as the modeling input. In the next approved stage, document and verify the actual differences—especially negation preservation—and select the text field and cleaning rules against the capstone objective. Separately confirm sentiment-label provenance before treating the labels as ground truth.

No source data or prior project files were modified. No packages were installed, and no model was trained.

## Command used

Run from the project root in PowerShell using the existing Python 3.14.7 interpreter:

```powershell
& 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe' '_text_readiness_temp.py'
```

The temporary audit script is intended to be removed after the report is generated; the only persistent change is this report.
