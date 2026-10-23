# E-commerce App Review Analytics

MBA NLP and Text Analytics capstone: **E-commerce App Review Analytics:
Sentiment Classification and Customer Experience Improvement**.

## Project status

The project input dataset is
`data/raw/google_play_reviews_processed.csv`, copied from an earlier project.
Its upstream preprocessing history is not fully verified. Here, “raw” means
the original input to this project; it does not necessarily mean untouched
source data from Google Play.

`data/processed/google_play_reviews_cleaned.csv` is generated from that input
by this project's reproducible cleaning pipeline. The source input is kept
unchanged; the cleaned file is a separate output.

## Setup decisions

- Keep original data read-only and out of version control by default.
- Keep intermediate data, processed data, and generated outputs separate from
  source code.
- Defer Python version and dependency configuration until the data format and
  approved implementation stage make those choices clear.
- Do not install packages or retrieve data as part of this stage.

See [PROJECT_PLAN.md](./PROJECT_PLAN.md) for the proposed staged workflow,
project structure, testing, and reproducibility requirements.

## Stage 1 verification

From the project root in PowerShell, run:

```powershell
Get-ChildItem -Force
Get-Content README.md
Get-Content PROJECT_PLAN.md
Get-Content .gitignore
```

Confirm that the plan remains present, this README and `.gitignore` exist, and
no dataset or analysis outputs have been added. Stage 1 is complete; wait for
approval before beginning data validation or other Stage 2 work.
