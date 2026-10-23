# Project Plan

## Project

**E-commerce App Review Analytics: Sentiment Classification and Customer
Experience Improvement**

## Current scope

This document proposes a staged, maintainable project structure and workflow.
At this stage, no analysis code, project directories, dependencies, datasets,
or reports are being created. Dataset details—including its source, schema,
coverage, and suitability—must be inspected and validated before they inform
implementation. No columns, findings, or model results are assumed here.

## Proposed project structure

```text
.
├── README.md                  # Project overview, setup, and run instructions
├── PROJECT_PLAN.md            # Stages, structure, and project requirements
├── pyproject.toml             # Project metadata and pinned/managed dependencies
├── .gitignore                 # Exclude local environments, data, and generated outputs
├── configs/
│   └── README.md              # Document configuration choices when introduced
├── data/
│   ├── raw/                   # Original source data; treated as read-only
│   ├── interim/               # Intermediate validated/cleaned data
│   └── processed/             # Analysis-ready data
├── notebooks/
│   └── README.md              # Optional, exploratory notebooks only
├── src/
│   └── review_analytics/
│       ├── __init__.py
│       ├── validation.py      # Input/schema and data-quality checks
│       ├── cleaning.py        # Documented text and record cleaning
│       ├── eda.py             # Descriptive and exploratory analysis
│       ├── sentiment.py       # Sentiment classification workflows
│       ├── issues.py          # Customer issue/theme analysis
│       ├── evaluation.py      # Evaluation helpers and metric reporting
│       └── visualizations.py  # Reusable plots
├── tests/
│   ├── test_validation.py
│   ├── test_cleaning.py
│   ├── test_sentiment.py
│   └── test_evaluation.py
└── outputs/
    ├── figures/               # Generated visualizations
    └── tables/                # Generated summary tables
```

The structure is intentionally small. Add modules or configuration files only
when an approved implementation stage needs them. Keep source data out of
version control by default; record its provenance and acquisition details
without committing private or restricted review data. Generated files should
be reproducible from code and documented inputs.

## Staged workflow

Each stage should be implemented and tested separately. Pause for approval
before moving to the next stage.

1. **Project setup and data intake** — agree on the data source and usage
   constraints; document provenance; establish a reproducible environment and
   confirm how the data can be accessed. Do not assume a schema in advance.
2. **Data validation** — inspect the actual file format and observed fields;
   check structural integrity, missingness, duplicates, types, and relevant
   quality issues. Report validation outcomes without silently changing data.
3. **Cleaning and preparation** — define and test transparent cleaning rules
   based on the observed data; preserve the raw input and track transformations.
4. **Exploratory data analysis** — summarize the available data and identify
   analysis limitations before selecting a modeling approach.
5. **Sentiment classification** — establish an appropriate baseline, define
   labeling and split strategy based on available labels and data, then assess
   candidate approaches. Avoid leakage between training and evaluation data.
6. **Customer issue analysis** — analyze recurring review topics or issues
   using methods justified by the data; distinguish observed themes from
   interpretation.
7. **Evaluation and visualization** — evaluate classification and issue
   analysis with suitable measures, document limitations, and create clear,
   reproducible visualizations.
8. **Final outputs and handoff** — after approval, assemble the requested
   outputs, explain how to reproduce them, and summarize evidence and
   limitations without overstating conclusions.

## Testing requirements

- Add focused unit tests for validation, cleaning, and evaluation behavior,
  including empty or malformed inputs and relevant boundary cases.
- Use small synthetic fixtures for tests so tests do not require the real
  dataset, network access, or large model downloads.
- Test that cleaning is deterministic and does not mutate or overwrite raw
  inputs.
- Test data-splitting and evaluation logic for leakage-prone mistakes where
  applicable.
- Keep tests runnable with one documented command; run relevant tests at each
  stage and record their outcomes.
- Treat data-dependent checks separately from unit tests and report failures
  explicitly rather than silently substituting defaults.

## Reproducibility requirements

- Document the Python version, environment setup, dependency management, and
  commands needed to run each approved stage.
- Pin or otherwise lock dependencies using the chosen project tooling; do not
  install dependencies until an implementation stage is approved.
- Make random seeds explicit for stochastic operations and record them.
- Keep configuration and transformation choices explicit; avoid hidden,
  machine-specific paths.
- Preserve raw data, track derived-data lineage, and document any external
  resources or model versions used.
- Record evaluation protocol and dataset split strategy so results can be
  regenerated and interpreted.
- Keep generated outputs separate from source code and identify which command
  produces each output.

## Approval checkpoint

Stop after this plan. No implementation stage should begin until the user
approves the next stage.
