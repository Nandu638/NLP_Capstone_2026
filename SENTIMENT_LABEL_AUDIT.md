# Sentiment Label Audit

**Dataset:** `data/raw/google_play_reviews_processed.csv`  
**Scope:** Read-only inspection of `review_text`, `rating`, `sentiment`, and
`clean_text`. No records were changed, relabeled, or removed.

## Observed rating-versus-sentiment counts

The table shows counts and row percentages, where each percentage is the
share of records with that sentiment among records with that rating.

| Rating | Row total | Negative | Neutral | Positive |
|---:|---:|---:|---:|---:|
| 1 | 1,562 | 1,562 (100.00%) | 0 (0.00%) | 0 (0.00%) |
| 2 | 249 | 249 (100.00%) | 0 (0.00%) | 0 (0.00%) |
| 3 | 279 | 0 (0.00%) | 279 (100.00%) | 0 (0.00%) |
| 4 | 438 | 0 (0.00%) | 0 (0.00%) | 438 (100.00%) |
| 5 | 3,312 | 0 (0.00%) | 0 (0.00%) | 3,312 (100.00%) |
| **Total** | **5,840** | **1,811** | **279** | **3,750** |

## Tested hypothesis

Tested the proposed rule as a hypothesis:

- ratings 1–2 map to `negative`
- rating 3 maps to `neutral`
- ratings 4–5 map to `positive`

**Observed result:** All 5,840 rows match the rule; there are **0 conflicting
rating-sentiment combinations** and no unassessable ratings or sentiment
labels in this dataset. The labels are therefore perfectly aligned with this
rating mapping in the inspected file.

This establishes the relationship present in the data, not how or why the
labels were assigned. In particular, perfect alignment alone does **not**
prove that the labels were generated from ratings.

## Text-field comparison

- Empty or whitespace-only `review_text` records: **0**.
- Empty or whitespace-only `clean_text` records: **0**.
- Records where `clean_text` differs exactly from `review_text`: **3,978 of
  5,840 (68.12%)**.
- Exact matches: **1,862 of 5,840 (31.88%)**.

The comparison is byte-for-character string equality after CSV decoding; it
does not establish whether differences are appropriate or what transformation
produced them. To avoid exposing personal information, no review contents are
quoted. As non-content examples, the first three differing records have
`review_text`/`clean_text` character lengths of **59/43**, **11/8**, and
**36/29**, respectively.

## Label provenance and limitations

Inspected the existing `PROJECT_PLAN.md`, `README.md`, and
`DATA_VALIDATION_REPORT.md`. These documents do not state who or what assigned
the sentiment labels, describe a labeling procedure, or cite a label source.
No other folders or external sources were searched. Label provenance remains
**unknown**.

This audit did not assess whether the text semantically expresses the assigned
sentiment, independently annotate reviews, or validate the correctness of
`clean_text`. The tested rating mapping is not treated as an established
sentiment definition.

## Recommendation

Do **not** treat the existing `sentiment` values as verified, independent
ground-truth sentiment labels for supervised sentiment classification until
their provenance and labeling method are confirmed. Their perfect
rating-category alignment raises the possibility that they encode a
rating-derived proxy, but this audit cannot determine their origin.

If the project intentionally studies prediction of rating categories from
review text, these labels could be considered a candidate weak/proxy target
only after documenting that objective and confirming the source. Any model
evaluated against them would measure agreement with these labels, not
necessarily sentiment understanding; independent human-labeled evaluation
would be needed to support that claim.

## Command used

Run from the project root in PowerShell with the existing VS Code Python
interpreter (Python 3.14.7):

```powershell
& 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe' '_audit_sentiment_temp.py'
```

The temporary, read-only audit script was removed after execution. The only
file created for this audit is `SENTIMENT_LABEL_AUDIT.md`.
