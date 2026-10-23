# E-commerce App Review Analytics: Sentiment Classification and Customer Experience Improvement

MBA NLP and Text Analytics capstone analyzing app reviews for Amazon Shopping, Flipkart, and Myntra. The project combines descriptive analysis, a text-only classification experiment against existing sentiment labels, keyword-based candidate issue detection, and a chi-square test of association.

## Objectives and research questions

The project aims to describe app, rating, existing-label, and review-length patterns; compare a text classifier with a majority-class baseline; summarize candidate issue matches; and identify customer-experience questions for further validation.

It asks:

1. What rating, existing-label, and review-length patterns appear in the available data?
2. How well does a text classifier agree with the existing labels compared with a majority-class baseline, and which classes remain difficult to predict?
3. Which reviews match configured issue-related keywords, and how do those candidate matches vary by app?
4. Is app name associated with the existing sentiment labels in this dataset?

## Dataset and preparation

The reports describe 5,840 English-language reviews for Amazon Shopping (1,964), Flipkart (1,900), and Myntra (1,976), with the observed data limited to India and one recorded collection timestamp.

The project input path is `data/raw/google_play_reviews_processed.csv`; the cleaned file is `data/processed/google_play_reviews_cleaned.csv`. Cleaning preserves the original rows and fields and appends `clean_text_new`, derived from `review_text` using Unicode NFC normalization, lowercasing, and whitespace standardization. The pipeline does not deliberately remove punctuation, numbers, URLs, or negation.

The data files are local-only and excluded from Git. The upstream source and preprocessing history are not fully verified; “raw” means the input to this project, not necessarily an untouched Google Play export. Confirm data rights and provenance separately.

## Methods and selected findings

- **Descriptive analysis:** Summarizes app, rating, existing-label, and review-length distributions. Rating 5 is the most frequent rating (3,312 records). The existing labels are positive for 3,750 records, negative for 1,811, and neutral for 279.
- **Sentiment-label classification:** A stratified 80/20 holdout (`random_state=42`) compares a majority-class baseline with TF-IDF unigram/bigram features and Logistic Regression. The baseline achieved 0.642123 accuracy and 0.260688 macro-F1; the model achieved 0.879281 accuracy and 0.591040 macro-F1. The classifier predicted **zero neutral records** in the 1,168-record test set (neutral support: 56).
- **Customer-issue analysis:** Configured keywords detect candidate matches in six themes: delivery and fulfilment (638), refunds and cancellations (335), customer support (291), app functionality (147), payment issues (115), and product quality (52). A review may match more than one theme.
- **App and existing-label association:** The chi-square test reported **χ²(4, N = 5,840) = 1460.74, p < .001, Cramér’s V = 0.354**. All nine expected counts were at least 5 and none was below 1. At α = .05, the null hypothesis of independence was rejected. This is an association in this dataset, not evidence of causation.

These findings are limited to the available data and documented methods. See the [final project report](FINAL_PROJECT_REPORT.md) for detailed results and interpretation.

## Limitations

- Sentiment-label provenance is unverified. Labels align exactly with the tested rating mapping: ratings 1–2 negative, rating 3 neutral, and ratings 4–5 positive. Model metrics and the chi-square test concern these existing labels, not independently validated sentiment.
- The classifier predicted zero neutral records in the holdout test set and should not be described as a reliable three-class sentiment classifier.
- Keyword matches are candidate themes, not validated complaints. Matches can occur in non-complaint contexts, and the method may miss unlisted wording.
- The chi-square test assumes independent observations; independence was not verified. The result indicates association, not causation or app quality.
- The results do not establish representativeness or generalization beyond these records, users, apps, locations, languages, or collection periods.
- A 500-character maximum is observed, but the available evidence does not establish truncation.
- The issue-review sample contains 13 annotated records, but its validation status conflicts with the documented pending status; annotation provenance is not recorded.

## Requirements and setup

No dependency or Python-version manifest is tracked. The repository does not specify a supported Python range, pinned dependency versions, or installation procedure. Python 3.14.7 is recorded as the environment used in existing reports, not as a declared compatibility guarantee.

The analysis modules require Matplotlib for EDA and issue analysis and scikit-learn for sentiment classification. The notebook also imports Pandas, IPython, and SciPy. Compatible versions are not pinned. A fresh clone is not a ready-to-run environment; prepare a compatible environment separately.

Data-dependent commands require local data you are authorized to use at the documented paths. The project makes no determination of data usage rights.

## Tests and reproduction

From the repository root in PowerShell, the documented test command is:

```powershell
python -m unittest discover -s tests -v
```

The tests use synthetic inputs. Existing reports record **24 tests passing with zero failures** in the original environment. This is a historical software-test result, not a fresh test run and not the chi-square statistical test.

The following commands match the existing script interfaces. Use a **new output root that does not already contain the target files**. Cleaning and sentiment analysis refuse existing destination files; issue analysis refuses if any of its target files already exists. EDA creates its output directories if needed but may overwrite files already present there.

```powershell
$python = 'python'
& $python 'src\review_analytics\cleaning.py' --input 'data\raw\google_play_reviews_processed.csv' --output 'outputs\reproduction\google_play_reviews_cleaned.csv'
& $python 'src\review_analytics\eda.py' --input 'outputs\reproduction\google_play_reviews_cleaned.csv' --figures-dir 'outputs\reproduction\eda-figures' --tables-dir 'outputs\reproduction\eda-tables'
& $python 'src\review_analytics\sentiment.py' --input 'outputs\reproduction\google_play_reviews_cleaned.csv' --results 'outputs\reproduction\sentiment_model_results.json'
$env:PYTHONPATH = 'src'
& $python -m review_analytics.issues --input 'outputs\reproduction\google_play_reviews_cleaned.csv' --tables-dir 'outputs\reproduction\issue-tables' --figures-dir 'outputs\reproduction\issue-figures'
```

Set `$python` to the Python interpreter for the prepared environment. These commands do not install dependencies. The issue-analysis command generates a pending-review sample; it does not reproduce the manual annotations in the local sample file.

`NLP_Capstone_Analysis.ipynb` contains 18 cells. Its data-loading cell loads the cleaned CSV and defines `reviews` before the later analysis and chi-square cells use it. Run the cells in order from the project root with the cleaned CSV available at the documented path.

## Project structure

Tracked project files include:

```text
.
├── README.md
├── PROJECT_PLAN.md
├── FINAL_PROJECT_REPORT.md
├── CLEANING_REPORT.md
├── DATA_VALIDATION_REPORT.md
├── EDA_REPORT.md
├── EDA_VERIFICATION_REPORT.md
├── ISSUE_ANALYSIS_REPORT.md
├── SENTIMENT_LABEL_AUDIT.md
├── SENTIMENT_MODEL_REPORT.md
├── TEXT_READINESS_AUDIT.md
├── src/
│   └── review_analytics/
│       ├── __init__.py
│       ├── cleaning.py
│       ├── eda.py
│       ├── issues.py
│       └── sentiment.py
└── tests/
    ├── test_cleaning.py
    ├── test_eda.py
    ├── test_issues.py
    └── test_sentiment.py
```

`NLP_Capstone_Analysis.ipynb` is present in the current working copy but is not currently tracked. The local `data/` and `outputs/` directories are excluded from Git and are not part of a fresh clone.

The scripts generate a cleaned CSV, EDA tables and figures, sentiment metrics JSON, and issue-analysis tables, figures, and a review sample. These outputs are local and are not available in a fresh public clone.

## Reports

- [Final project report](FINAL_PROJECT_REPORT.md)
- [Data validation report](DATA_VALIDATION_REPORT.md)
- [Cleaning report](CLEANING_REPORT.md)
- [EDA report](EDA_REPORT.md) and [EDA verification report](EDA_VERIFICATION_REPORT.md)
- [Sentiment-label audit](SENTIMENT_LABEL_AUDIT.md) and [text readiness audit](TEXT_READINESS_AUDIT.md)
- [Sentiment model report](SENTIMENT_MODEL_REPORT.md)
- [Issue analysis report](ISSUE_ANALYSIS_REPORT.md)
- [Project plan](PROJECT_PLAN.md)
