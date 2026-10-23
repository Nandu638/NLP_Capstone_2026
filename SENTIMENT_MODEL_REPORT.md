# Sentiment Classification Experiment Report

## Scope and target interpretation

This experiment uses `data/processed/google_play_reviews_cleaned.csv`,
`clean_text_new` as the **only feature**, and the existing `sentiment` column
as the target. App name, rating, package ID, and all other metadata were
excluded from model features.

The sentiment-label audit found perfect alignment with the tested rating
mapping: ratings 1–2 are labeled `negative`, rating 3 `neutral`, and ratings
4–5 `positive`. The labels' historical provenance remains unverified.
Accordingly, all reported metrics measure agreement with these existing
rating-aligned labels—not independent validation of true customer sentiment.

## Data and split

- Input records: **5,840**; no rows were dropped.
- Target counts: `negative` **1,811**, `neutral` **279**, `positive` **3,750**.
- Split: stratified 80% train / 20% test using `random_state=42`.
- Training records: **4,672** (`negative` 1,449; `neutral` 223; `positive`
  3,000).
- Test records: **1,168** (`negative` 362; `neutral` 56; `positive` 750).
- The TF-IDF vectorizer is part of a scikit-learn pipeline fitted only on the
  training partition, preventing test text from contributing to vocabulary or
  inverse-document-frequency fitting.

## Models and settings

1. **Majority-class baseline:** predict the most frequent training label for
   every test record. The selected label was `positive`.
2. **Text classifier:** TF-IDF unigram/bigram features followed by
   multinomial Logistic Regression as implemented by scikit-learn's
   `LogisticRegression`.

TF-IDF settings: `ngram_range=(1, 2)`, `min_df=1`, `max_features=50000`,
`sublinear_tf=True`, `lowercase=False` (the input text is already lowercased).
Classifier settings: `max_iter=1000`, `random_state=42`, default `class_weight`
(`None`). No model or vocabulary was fitted using test records.

## Evaluation results

| Metric | Majority baseline | TF-IDF + Logistic Regression |
|---|---:|---:|
| Accuracy | 0.642123 | 0.879281 |
| Macro precision | 0.214041 | 0.578136 |
| Macro recall | 0.333333 | 0.604594 |
| Macro F1 | 0.260688 | 0.591040 |

### Per-class metrics and test support

| Model | Class | Precision | Recall | F1 | Support |
|---|---|---:|---:|---:|---:|
| Majority baseline | negative | 0.000000 | 0.000000 | 0.000000 | 362 |
| Majority baseline | neutral | 0.000000 | 0.000000 | 0.000000 | 56 |
| Majority baseline | positive | 0.642123 | 1.000000 | 0.782065 | 750 |
| TF-IDF + Logistic Regression | negative | 0.833780 | 0.859116 | 0.846259 | 362 |
| TF-IDF + Logistic Regression | neutral | 0.000000 | 0.000000 | 0.000000 | 56 |
| TF-IDF + Logistic Regression | positive | 0.900629 | 0.954667 | 0.926861 | 750 |

### Confusion matrices

Rows are true labels and columns are predicted labels; order is
`negative`, `neutral`, `positive`.

**Majority baseline**

| True \ Predicted | Negative | Neutral | Positive |
|---|---:|---:|---:|
| Negative | 0 | 0 | 362 |
| Neutral | 0 | 0 | 56 |
| Positive | 0 | 0 | 750 |

**TF-IDF + Logistic Regression**

| True \ Predicted | Negative | Neutral | Positive |
|---|---:|---:|---:|
| Negative | 311 | 0 | 51 |
| Neutral | 28 | 0 | 28 |
| Positive | 34 | 0 | 716 |

The classifier predicted **zero** neutral test records. Its neutral-class
precision, recall, and F1 are all **0.000000** (support 56). This is important
despite its overall accuracy and positive/negative performance.

## Interpretation and limitations

The positive class is the largest class (**3,750 / 5,840 = 64.21%** of the
full data). A majority-only predictor therefore reaches **64.21%** accuracy
while having zero recall for negative and neutral classes and a macro-F1 of
0.260688 on this test split. This illustrates why accuracy alone can obscure
poor minority-class performance. The TF-IDF model's accuracy is higher, but
its failure to predict any neutral examples remains a material limitation;
macro metrics and per-class results expose that.

This is a single stratified holdout experiment with one fixed seed, not
cross-validation or a hyperparameter search. The apparent performance is
agreement with the existing labels. Since sentiment labels align perfectly
with rating categories and their origin is not documented, these scores do
not demonstrate independent sentiment understanding or generalization to
true customer sentiment. The split is random by review, not grouped by user,
app, or time; such generalization questions were not evaluated. No EDA,
topic modeling, customer-issue analysis, or business recommendations were
performed in this stage.

## Saved experiment record

The reproducible settings and complete metric results (including class
support and confusion matrices) are saved in
`outputs/tables/sentiment_model_results.json`. The record includes the input
path and SHA-256, feature/target names, split seed and sizes, class counts,
model settings, and evaluation metrics. It does not contain a fitted model
artifact.

## Tests and reproduction

Focused synthetic tests cover deterministic stratification, class proportions,
pipeline fitting without using held-out text for vectorizer vocabulary,
metric calculations, confusion matrix and support, and saving the experiment
record without metadata features. All existing project tests were run:
**16 tests passed, 0 failures**.

Using the existing Python 3.14.7 environment, run from the project root in
PowerShell:

```powershell
& 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe' -m unittest discover -s tests -v
& 'C:\Users\nanda\AppData\Local\Python\pythoncore-3.14-64\python.exe' 'src\review_analytics\sentiment.py'
```

The experiment command refuses to overwrite an existing results JSON file.
Required libraries (`scikit-learn`, NumPy, SciPy, and joblib) were already
available; no packages were installed.
