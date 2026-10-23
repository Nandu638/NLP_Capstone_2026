# E-commerce App Review Analytics: Sentiment Classification and Customer Experience Improvement

## Project overview

This capstone consolidates a descriptive and predictive analysis of **5,840
English-language app reviews** for Amazon Shopping, Flipkart, and Myntra. The
project examines the observed rating and sentiment-label distributions,
review-text characteristics, a TF-IDF/Logistic Regression classifier trained
against the dataset's existing labels, and keyword-based candidate customer
issues.

The source file is named
[`data/raw/google_play_reviews_processed.csv`](data/raw/google_play_reviews_processed.csv).
Project documentation describes it as the original input to this project, but
its upstream preprocessing history is not fully verified; “raw” should not be
read as proof that the file is an untouched Google Play export. The analysis
uses the separately prepared
[`data/processed/google_play_reviews_cleaned.csv`](data/processed/google_play_reviews_cleaned.csv).
The reported results are limited to these files and the documented methods.

The evidence supports descriptive observations about this dataset and a
single held-out agreement assessment against its existing labels. It does not
establish independently verified customer sentiment, validated complaint
prevalence, causal app effects, or results representative of all app users.

## Research objectives

1. Describe the dataset's app, rating, existing sentiment-label, and
   review-length distributions.
2. Evaluate a text-only classifier's agreement with the dataset's existing
   sentiment labels, using a majority-class baseline and a stratified
   holdout.
3. Identify review records containing configured issue-related keywords and
   summarize these candidate matches overall and by app.
4. Translate the observed patterns into cautious customer-experience
   considerations while stating the limits of the evidence.

## Dataset and preparation

### Dataset profile

The validation report records **5,840 records and 14 source columns**. There
are 1,964 Amazon Shopping, 1,900 Flipkart, and 1,976 Myntra records. The
observed country and language fields contain only `in` and `en`, respectively;
the collection timestamp is the same across the rows. Thus the analysis is
not evidence about other countries, languages, collection periods, or the
broader populations of app users.

The rating counts are 1,562 at rating 1, 249 at rating 2, 279 at rating 3,
438 at rating 4, and 3,312 at rating 5. The existing sentiment column has
1,811 `negative`, 279 `neutral`, and 3,750 `positive` records. The validation
report records 763 missing values in `review_version`; it records no missing
`review_text`, no exact duplicate rows, and no malformed-width records.

### Text preparation

The cleaning pipeline reads `review_text`, applies Unicode NFC normalization,
lowercases, and standardizes whitespace. It appends `clean_text_new` while
preserving the original columns and records. The cleaning report records
5,840 input and output rows, zero excluded rows, and 2,379 rows whose new text
differs from the original. Punctuation, numbers, URLs, and negation are not
deliberately removed by this pipeline. EDA length calculations use
`clean_text_new`, not the older `clean_text` field.

### Sentiment-label provenance

The existing labels align perfectly in the inspected data with the tested
rating mapping: ratings 1–2 are labeled negative, rating 3 neutral, and
ratings 4–5 positive (5,840 matches, zero conflicts). However, the available
project files do not establish who or what assigned the labels or how they
were derived. **Sentiment-label provenance is unverified.** Perfect alignment
does not prove that labels were generated from ratings, nor that they are
independent annotations of the review text. This limitation governs the
interpretation of all model metrics below.

## Exploratory data analysis

### Ratings and existing labels

Rating 5 accounts for 3,312 of 5,840 records (56.71%); rating 1 accounts for
1,562 (26.75%). The remaining counts are 249 at rating 2, 279 at rating 3,
and 438 at rating 4. Existing labels are 64.21% positive (3,750), 31.01%
negative (1,811), and 4.78% neutral (279). These are distributions of
observed ratings and labels, not independently verified measures of review
sentiment.

App-level rating and label mixes differ in this dataset. For example, the
share of rating-5 records is 27.70% for Amazon Shopping, 65.95% for Flipkart,
and 76.67% for Myntra. The share carrying the existing positive label is
31.62%, 76.79%, and 84.51%, respectively. The complete counts and
within-app percentages are in
[`outputs/tables/app_rating_counts.csv`](outputs/tables/app_rating_counts.csv)
and
[`outputs/tables/app_sentiment_counts.csv`](outputs/tables/app_sentiment_counts.csv).
Because the labels are rating-aligned and their provenance is unverified,
label percentages should not be presented as validated sentiment estimates.

### Association between app and existing sentiment labels

A Pearson chi-square test of independence assessed the association between
`app_name` and the existing `sentiment` labels. The null hypothesis is that
app name and existing sentiment label are independent; the alternative
hypothesis is that they are associated. The observed contingency table was:

| App | Negative | Neutral | Positive | Total |
|---|---:|---:|---:|---:|
| Amazon Shopping | 1,208 | 135 | 621 | 1,964 |
| Flipkart | 325 | 116 | 1,459 | 1,900 |
| Myntra | 278 | 28 | 1,670 | 1,976 |
| **Total** | **1,811** | **279** | **3,750** | **5,840** |

The chi-square test indicated a statistically significant association
between app name and the existing sentiment labels, χ²(4, N = 5,840) =
1460.74, p < .001, Cramér’s V = 0.354. Cramér’s V is an effect-size measure
that summarizes the strength of association between categorical variables.
It does not establish causation. None of the 9 expected cell counts was
below 1, and all 9 were at least 5. At α = .05, the null hypothesis is
rejected: app name is associated with the existing sentiment labels in this
dataset. Independence of observations is assumed, not verified.

This result concerns the existing labels only. Their provenance is
unverified, and they align exactly with the tested rating mapping (ratings
1–2 negative, 3 neutral, and 4–5 positive). The test does not establish
independently validated sentiment, causation, or generalization beyond this
dataset.

### Review length

Across the 5,840 `clean_text_new` values, mean length is 82.77 characters
(median 22; 95th percentile 425.05; range 2–500) and mean length is 15.05
whitespace-separated tokens (median 4; 95th percentile 75; range 1–106).
The longest observed values are 500 characters; the EDA verification report
found 23 source reviews at that length and no longer ones. The files do not
establish whether this pattern reflects an upstream limit or natural review
lengths, so truncation is not asserted.

The EDA figures are
[`outputs/figures/rating_distribution.png`](outputs/figures/rating_distribution.png),
[`outputs/figures/sentiment_distribution.png`](outputs/figures/sentiment_distribution.png),
[`outputs/figures/app_comparison.png`](outputs/figures/app_comparison.png),
and
[`outputs/figures/review_length_by_app.png`](outputs/figures/review_length_by_app.png).
The corresponding result tables are
[`outputs/tables/app_counts.csv`](outputs/tables/app_counts.csv),
[`outputs/tables/rating_counts.csv`](outputs/tables/rating_counts.csv),
[`outputs/tables/sentiment_counts.csv`](outputs/tables/sentiment_counts.csv),
[`outputs/tables/rating_sentiment_counts.csv`](outputs/tables/rating_sentiment_counts.csv),
and
[`outputs/tables/review_length_summary.csv`](outputs/tables/review_length_summary.csv).

## Sentiment-classification methodology and results

### Protocol

The experiment uses `clean_text_new` as its only feature and the existing
`sentiment` column as its target; app name, rating, and other metadata are
excluded. It splits all 5,840 records into a stratified 80% training set
(4,672) and 20% test set (1,168), with `random_state=42`. The training split
contains 1,449 negative, 223 neutral, and 3,000 positive records; the test
split contains 362 negative, 56 neutral, and 750 positive records.

The baseline predicts the most frequent training label for every test
record. The text model uses TF-IDF unigram and bigram features
(`min_df=1`, maximum 50,000 features, sublinear term frequency, and no
additional lowercasing) followed by scikit-learn multinomial Logistic
Regression (`max_iter=1000`, `random_state=42`, default class weighting).
The saved experiment record states that the vectorizer was fitted on training
text only.

### Held-out results

| Metric | Majority-class baseline | TF-IDF + Logistic Regression |
|---|---:|---:|
| Accuracy | 0.642123 | 0.879281 |
| Macro precision | 0.214041 | 0.578136 |
| Macro recall | 0.333333 | 0.604594 |
| Macro F1 | 0.260688 | 0.591040 |

For Logistic Regression, negative-class precision, recall, and F1 are
0.833780, 0.859116, and 0.846259 (support 362); positive-class values are
0.900629, 0.954667, and 0.926861 (support 750). For the neutral class
(support 56), precision, recall, and F1 are all **0.000000**. Its confusion
matrix has no neutral predictions: it predicted **zero neutral test records**.
The baseline also predicted zero neutral records.

Accordingly, despite the higher overall accuracy than the baseline, this
Logistic Regression model **must not be described as a reliable three-class
sentiment classifier**. In particular, its reported aggregate scores conceal
complete failure to identify neutral records in this test split.

The machine-readable results, including per-class measures, support,
confusion matrices, split counts, and settings, are in
[`outputs/tables/sentiment_model_results.json`](outputs/tables/sentiment_model_results.json).
The metrics measure agreement with the existing labels only. Given their
unverified provenance and exact rating alignment, they do **not** establish
independently verified sentiment accuracy or understanding. The experiment is
one stratified random holdout with one seed; it does not assess stability
across seeds, time, users, or app-grouped splits.

## Customer issue analysis

The issue detector searches review text for configured terms in six themes:
delivery and fulfilment, customer support, refunds and cancellations, app
functionality, product quality, and payment issues. Each review contributes
at most once to a theme, but may match several themes. Counts are therefore
overlapping. These figures are **keyword-based candidate matches, not
confirmed complaints**; terms may occur in positive, neutral, ambiguous, or
otherwise non-complaint contexts, and the method can miss paraphrases and
unlisted wording.

| Candidate theme | Matching reviews | Dataset denominator | Candidate-match rate |
|---|---:|---:|---:|
| Delivery and fulfilment | 638 | 5,840 | 10.92% |
| Refunds and cancellations | 335 | 5,840 | 5.74% |
| Customer support | 291 | 5,840 | 4.98% |
| App functionality | 147 | 5,840 | 2.52% |
| Payment issues | 115 | 5,840 | 1.97% |
| Product quality | 52 | 5,840 | 0.89% |

In the app-level candidate-match table, delivery rates are 16.65% for Amazon
Shopping, 6.53% for Flipkart, and 9.46% for Myntra. Refund/cancellation rates
are 8.45%, 2.74%, and 5.92%, respectively. These are shares of each app's
reviews matching the configured terms; they are not validated complaint
rates. Full results are in
[`outputs/tables/issue_theme_counts.csv`](outputs/tables/issue_theme_counts.csv)
and
[`outputs/tables/issue_theme_by_app.csv`](outputs/tables/issue_theme_by_app.csv).
The associated figures are
[`outputs/figures/issue_theme_prevalence.png`](outputs/figures/issue_theme_prevalence.png)
and
[`outputs/figures/issue_theme_by_app.png`](outputs/figures/issue_theme_by_app.png).

### Limited manual review and discrepancy

The existing
[`outputs/tables/issue_review_sample.csv`](outputs/tables/issue_review_sample.csv)
contains **13 review rows** and row-level candidate-theme annotations,
validation statuses, and notes. This is the only manually reviewed sample
described by the project evidence; it is not full-dataset theme validation
and cannot establish the precision or recall of the keyword detector across
all 5,840 reviews.

There is a file-level discrepancy worth preserving: the issue-analysis
report describes the sample as pending human review, and the current issue
analysis code/tests generate sample rows marked as pending; the checked-in
sample file, by contrast, contains supported/unsupported/uncertain
annotations. The aggregate issue tables still mark every theme as “not
validated.” The source files do not record who made or when they made the
sample annotations. This report therefore acknowledges the 13 annotated
records, treats aggregate counts as candidate matches, and does not treat the
sample as evidence that the full dataset's themes have been validated.

## Business implications

The observed label and candidate-keyword differences may help prioritize
questions for further investigation—for example, checking fulfilment,
refund/cancellation, and support experiences in a larger, carefully
validated sample. The comparatively high Amazon Shopping candidate-match
rates for several operational terms, and the different app-level rating
mixes, are descriptive signals in this dataset only. They do not explain why
the differences occur, establish a causal app effect, or show that one app
provides a better experience for its entire customer base.

The current classifier should not be used to make operational decisions as a
three-class sentiment system because it predicted no neutral test records
and was evaluated against labels of unverified provenance. Before using any
issue or sentiment result for prioritization, a business team should validate
the underlying review interpretations with a larger, documented human review
and confirm that the sample and collected reviews reflect the intended
customer population.

## Limitations and future improvements

1. **Data provenance and coverage:** upstream dataset acquisition and
   preprocessing are not fully established. The observed data are limited to
   three apps, English, India, and one recorded collection timestamp; coverage
   and representativeness beyond these files are unknown.
2. **Label validity:** the sentiment-label source and assignment method are
   unverified, and labels match rating categories exactly. Obtain documented
   label provenance or create independently annotated sentiment labels with
   a clear annotation guide and adjudication process.
3. **Classifier performance:** the model predicts no neutral test records.
   Collect or verify adequate neutral examples, examine class-aware
   alternatives, and evaluate with repeated or cross-validated protocols and
   independent labels before considering deployment.
4. **Generalization:** a single random review-level split does not test
   generalization across time, users, or apps. Where identifiers and data
   volume permit, use temporal, group-aware, and app-held-out evaluation.
5. **Issue detection:** configured keyword matches are not contextual
   complaint classifications. Expand and document the annotation sample,
   use multiple reviewers and agreement checks, evaluate a representative
   held-out set, and consider context-aware methods only with validated
   labels.
6. **Sample discrepancy:** the 13-row sample's annotations conflict with
   the pending-validation status documented by the report and implemented by
   the generator. Record annotation provenance and update the reporting
   workflow before relying on sample-level validation statistics.
7. **Text limits and preparation:** the observed 500-character maximum has
   no established upstream explanation. Confirm source-side handling and
   assess whether transformations preserve useful context before changing
   the text pipeline.
8. **Business evidence:** the analysis is descriptive and observational.
   Test proposed interventions with appropriate operational data and
   evaluation designs before making causal or app-wide claims.

## Conclusion

The inspected project files consistently support the dataset's main
distribution counts, the saved holdout experiment metrics, and the overall
keyword-candidate counts. The TF-IDF/Logistic Regression run improves
agreement over the majority baseline on overall and macro metrics, but its
zero neutral predictions prevent it from being characterized as a reliable
three-class classifier. Candidate issue matches suggest areas for further
review, not verified complaint prevalence. All app comparisons remain
descriptive and cannot establish causation or represent all app users.

Most importantly, the existing labels' provenance is unverified; model
metrics describe agreement with those labels rather than independently
verified customer sentiment. Only 13 reviews have annotations in the
available issue-review sample, and the conflicting pending/not-validated
records limit what can be concluded from that sample.

## Evidence and references

No external references or evidence of a literature review were present in the
project files inspected. This report makes no claim that external literature
was reviewed. Its evidence base is the project data, output tables and JSON,
figures, source modules, tests, and existing stage reports:

- [`README.md`](README.md)
- [`DATA_VALIDATION_REPORT.md`](DATA_VALIDATION_REPORT.md)
- [`CLEANING_REPORT.md`](CLEANING_REPORT.md)
- [`EDA_REPORT.md`](EDA_REPORT.md)
- [`EDA_VERIFICATION_REPORT.md`](EDA_VERIFICATION_REPORT.md)
- [`SENTIMENT_LABEL_AUDIT.md`](SENTIMENT_LABEL_AUDIT.md)
- [`TEXT_READINESS_AUDIT.md`](TEXT_READINESS_AUDIT.md)
- [`SENTIMENT_MODEL_REPORT.md`](SENTIMENT_MODEL_REPORT.md)
- [`ISSUE_ANALYSIS_REPORT.md`](ISSUE_ANALYSIS_REPORT.md)
- [`src/review_analytics/cleaning.py`](src/review_analytics/cleaning.py),
  [`src/review_analytics/eda.py`](src/review_analytics/eda.py),
  [`src/review_analytics/sentiment.py`](src/review_analytics/sentiment.py),
  and [`src/review_analytics/issues.py`](src/review_analytics/issues.py)
- Tests: [`tests/test_cleaning.py`](tests/test_cleaning.py),
  [`tests/test_eda.py`](tests/test_eda.py),
  [`tests/test_sentiment.py`](tests/test_sentiment.py), and
  [`tests/test_issues.py`](tests/test_issues.py)

## Reproducibility instructions

The existing reports specify Python 3.14.7 and the following interpreter on
the original machine:
`C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe`.
Use the corresponding installed interpreter in the project environment. The
project reports record that the complete test suite passed **24 tests with
zero failures**. This result is taken from the existing
[`ISSUE_ANALYSIS_REPORT.md`](ISSUE_ANALYSIS_REPORT.md); tests and analyses
were not rerun while preparing this consolidation.

From the project root in PowerShell, the test command recorded by the stage
reports is:

```powershell
$python = 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe'
& $python -m unittest discover -s tests -v
```

To regenerate the analysis in a fresh output location without overwriting
the current result artifacts, use the existing script entry points and
separate destinations. These commands are provided for future reproduction;
they were **not run** for this report:

```powershell
$python = 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe'
& $python 'src\review_analytics\cleaning.py' --input 'data\raw\google_play_reviews_processed.csv' --output 'outputs\reproduction\google_play_reviews_cleaned.csv'
& $python 'src\review_analytics\eda.py' --input 'outputs\reproduction\google_play_reviews_cleaned.csv' --figures-dir 'outputs\reproduction\eda-figures' --tables-dir 'outputs\reproduction\eda-tables'
& $python 'src\review_analytics\sentiment.py' --input 'outputs\reproduction\google_play_reviews_cleaned.csv' --results 'outputs\reproduction\sentiment_model_results.json'
$env:PYTHONPATH = 'src'
& $python -m review_analytics.issues --input 'outputs\reproduction\google_play_reviews_cleaned.csv' --tables-dir 'outputs\reproduction\issue-tables' --figures-dir 'outputs\reproduction\issue-figures'
```

The cleaning, EDA, sentiment, and issue-analysis scripts refuse to overwrite
existing destinations. The issue-analysis generator creates a pending-review
sample; it does not reproduce the manual annotations currently present in
[`outputs/tables/issue_review_sample.csv`](outputs/tables/issue_review_sample.csv).
The saved experiment JSON records the cleaned input SHA-256 as
`b932e2589ec49fbcbe54532b93cfadd23f4f4e549b3bb9af91cdc911be3e63b1`.
No package installation is part of these instructions.
