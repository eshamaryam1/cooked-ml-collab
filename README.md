# cooked-ml

Reproducible California Housing price regression pipeline — the shared MLOps assignment repo for
team **cooked** (Esha + Nimra).

The pipeline trains scikit-learn models on the California Housing dataset with a deterministic
train/test split and preprocessing fit on the training split only, then reports the two metrics
the team tracks: **r2** and **MAE**.

## Dataset

- **California Housing** — 20,640 rows × 9 columns, target `MedHouseVal` (in units of $100,000).
- Fetched once via `sklearn.datasets.fetch_california_housing` and written to a deterministic
  `data/raw/california_housing.csv` (fixed column order, `%.10g` floats, `\n` line endings), so
  both machines produce byte-identical data.
- Starter code adapted from
  [`mikel-brostrom/Housing_Price_Prediction`](https://github.com/mikel-brostrom/Housing_Price_Prediction)
  — credited in full in `REPORT.md`. We keep the dataset, the model families and the metrics, and
  drop the PyTorch network so everything stays on scikit-learn.

Raw data and trained models are **never** committed to Git; they are tracked by DVC (Module 04).

## Layout

```
.
├── configs/smoke.yaml      # reduced-parameter smoke variant of params.yaml
├── data/raw/               # raw CSV + sklearn cache (DVC-tracked, gitignored)
├── models/                 # trained model + metrics (DVC-tracked, gitignored)
├── src/cooked_ml/
│   ├── config.py           # load_params() — every value comes from params.yaml
│   ├── data.py             # load_raw, ensure_raw_dataset, build_splits, save_splits
│   ├── features.py         # make_preprocessor() — scaler fitted on train only
│   ├── models.py           # build_pipeline() — random_forest | linear_regression | ...
│   └── cli.py              # argparse entry point: train | evaluate
├── tests/                  # pytest suite + fixtures
├── docs/                   # module plan, playbook, progress tracker
├── params.yaml             # single source of truth for every experiment knob
└── pyproject.toml          # uv project, pinned by uv.lock
```

## Setup

Requires [`uv`](https://docs.astral.sh/uv/) — it manages its own Python, so no system install is
needed.

```bash
git clone https://github.com/eshamaryam1/cooked-ml-collab.git
cd cooked-ml-collab
uv sync                 # creates .venv from the committed uv.lock
```

## Run

```bash
uv run python -m cooked_ml.cli train        # fetch data, fit, save model + metrics
uv run python -m cooked_ml.cli evaluate     # score the saved model on the test split
```

Both commands read `params.yaml` from the repo root; override with `--params` / `--data`.

```bash
uv run python -m cooked_ml.cli --params configs/smoke.yaml train   # fast smoke run
uv run pytest tests/                       # test suite
uv run ruff check && uv run ruff format --check .   # lint + format gate
```

Baseline (random forest, seed 42, 20% test split): **r2 0.8074, MAE 0.3259**.

## Reproduce with DVC

Once Module 04 lands:

```bash
dvc pull        # fetch the raw CSV and model from the DVC remote
dvc repro       # rebuild every pipeline stage
dvc exp show    # compare experiments
```

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`docs/PLAYBOOK.md`](docs/PLAYBOOK.md)` before your
first PR: branch model, Conventional Commits, merge strategy and the review rules.
Progress is tracked in [`docs/PROGRESS.md`](docs/PROGRESS.md).
