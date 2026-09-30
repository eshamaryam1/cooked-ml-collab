# Module 06 — A reproducible pipeline

**Owner:** Esha (Model owner), reviewed by Nimra
**Depends on:** Module 05 (features already promoted into `src/`)
**Branch:** `feat/dvc-pipeline` → PR into `dev`
**Checkpoint:** a teammate on a fresh clone runs `dvc pull && dvc repro` and gets identical metrics

---

## Goal

All hyperparameters in `params.yaml`, the code split into `prepare` / `train` / `evaluate`, wired
together in `dvc.yaml`, seeded everywhere, preprocessing fit on training data only, and the commit
SHA logged with every run.

## Steps

### 1. Branch

```bash
git switch dev
git pull --ff-only
git switch -c feat/dvc-pipeline
uv run dvc pull
```

### 2. `params.yaml` at the repo root

```yaml
seed: 42

data:
  raw: data/raw/california_housing.csv
  processed_dir: data/processed
  drop_duplicates: true

split:
  test_size: 0.2

preprocess:
  standardize: true

train:
  model: random_forest
  n_estimators: 100
  max_depth: 6
  min_samples_leaf: 1

evaluate:
  metrics: [r2, mae]
```

`configs/smoke.yaml` is the same file with a tiny sample size, for CI (Module 08):

```yaml
seed: 42

data:
  raw: data/raw/california_housing.csv
  processed_dir: data/processed
  smoke_rows: 500
  drop_duplicates: true

split:
  test_size: 0.2

preprocess:
  standardize: true

train:
  model: random_forest
  n_estimators: 20
  max_depth: 6

evaluate:
  metrics: [r2, mae]
```

### 3. Seeds everywhere

One helper, used by every stage:

```python
# src/cooked_ml/config.py
import os
import random

import numpy as np


def set_global_seed(seed: int) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
```

Call it as the first thing in each stage. `PYTHONHASHSEED` only takes effect for the process that
reads it, so also export it before invoking DVC:

```bash
# PowerShell, per stage run
$env:PYTHONHASHSEED = "42"
```

Randomness to control: `train_test_split(random_state=seed)`, `RandomForestRegressor(random_state=seed)`,
`shuffle` in any sampler, any `np.random.*` call, torch if we ever reintroduce it.

Also set `n_jobs` explicitly in the forest so parallel float summation cannot reorder between
machines:

```python
RandomForestRegressor(random_state=seed, n_jobs=1, ...)
```

### 4. Stages

**`prepare`** — `python -m cooked_ml.cli prepare`

1. Load `data/raw/california_housing.csv`.
2. Optionally drop exact duplicates (`data.drop_duplicates`).
3. Stratify-free but seeded split: `train_test_split(df, test_size=0.2, random_state=42)`.
4. Fit the preprocessor on the **training rows only**, then transform both.
5. Write `data/processed/train.csv`, `data/processed/test.csv`, and the fitted transformer to
   `models/preprocessor.joblib`.

This is the leakage fix. The starter code scaled the whole dataset first. Assert it in a test:

```python
# tests/test_data.py
def test_scaler_is_fit_on_training_rows_only():
    from sklearn.preprocessing import StandardScaler
    from cooked_ml.data import build_splits
    from cooked_ml.features import make_preprocessor

    df = load_raw("data/raw/california_housing.csv").head(2000)
    train, test = build_splits(df, test_size=0.2, seed=42)
    pre = make_preprocessor({"standardize": True})
    pre.fit(train[FEATURES])

    train_means = train[FEATURES].mean().to_numpy()
    scaler_means = pre.named_steps["scaler"].mean_

    np.testing.assert_allclose(train_means, scaler_means, rtol=1e-9)
```

**`train`** — `python -m cooked_ml.cli train`

```python
from sklearn.pipeline import Pipeline

model = Pipeline([("pre", load("models/preprocessor.joblib")), ("clf", build_model(cfg, seed))])
model.fit(pd.read_csv("data/processed/train.csv"), y)
joblib.dump(model, "models/model.joblib")
```

Using a single fitted `Pipeline` object means inference cannot accidentally skip the transform.

**`evaluate`** — `python -m cooked_ml.cli evaluate`

Loads `models/model.joblib` and `data/processed/test.csv`, computes R² and MAE (the two metrics the
starter repo reports), and writes `metrics.json`:

```json
{
  "r2": 0.8157,
  "mae": 0.2812,
  "n_train": 16512,
  "n_test": 4128,
  "seed": 42,
  "commit_sha": "3f9a1c2...",
  "params": {
    "model": "random_forest",
    "n_estimators": 100,
    "max_depth": 6,
    "test_size": 0.2
  },
  "data": {
    "raw_dvc_hash": "d3f07384d113edec49eaa6238ad5ff00",
    "raw_dvc_md5": "d3f07384d113edec49eaa6238ad5ff00"
  },
  "dvc_lock_md5": "9e2b1a...",
  "timestamp": "2026-01-01T00:00:00Z"
}
```

Logging the commit SHA (assignment step 5) — minimal and dependency-free:

```python
def current_commit_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"
```

Do not add MLflow or W&B for this module. The assignment says the SHA in `metrics.json` is the
minimum, and fewer moving parts means the reproduction checkpoint is easier to hit. If time
remains after Module 09, adding W&B is a bonus.

Note the `timestamp`: it makes `metrics.json` differ between runs even when the numbers match.
Two options — pin it to the commit date, or drop it. **Drop it.** Exclude the whole metrics file
from DVC's hash by writing it with a fixed key order and no volatile fields; if we want a
timestamp, keep it out of the tracked content.

### 5. `dvc.yaml`

```yaml
stages:
  prepare:
    cmd: uv run python -m cooked_ml.cli prepare
    deps:
      - data/raw/california_housing.csv
      - src/cooked_ml/data.py
      - src/cooked_ml/features.py
      - src/cooked_ml/config.py
      - params.yaml
    outs:
      - data/processed/train.csv
      - data/processed/test.csv
      - models/preprocessor.joblib

  train:
    cmd: uv run python -m cooked_ml.cli train
    deps:
      - data/processed/train.csv
      - src/cooked_ml/models.py
      - params.yaml
    outs:
      - models/model.joblib

  evaluate:
    cmd: uv run python -m cooked_ml.cli evaluate
    deps:
      - models/model.joblib
      - data/processed/test.csv
      - params.yaml
      - dvc.yaml
    metrics:
      - metrics.json:
          cache: false
```

`cache: false` on the metrics means the numbers are visible in `dvc.lock` and in Git, which is what
a reviewer wants to see. (We only do this once we are off DVC 3.x's deprecated
`dvcm`/`yaml` syntax; with modern DVC the simple form above is correct.)

Everything in `deps` that lives under `src/` must be listed — that is what makes `dvc repro`
re-run when code changes. Forgetting `src/` in `deps` is the classic way to end up with a stale
model.

Track model artefacts with DVC, not Git:

```bash
uv run dvc add models/preprocessor.joblib models/model.joblib
```

Check the size first — `RandomForestRegressor` with 100 trees on 16k rows is roughly 30-80 MB.
If it is large, use fewer trees for the CI smoke config and reduce `n_estimators` in
`params.yaml` for the main run too. Our DagsHub quota is small, so prefer 100 trees with
`max_depth=6`.

### 6. Run, push, commit

```bash
uv run dvc repro
cat metrics.json
uv run pytest tests/ -q
uv run dvc push
git add dvc.yaml dvc.lock params.yaml metrics.json .gitignore
git commit -m "feat: add seeded dvc pipeline producing reproducible metrics"
git push -u origin feat/dvc-pipeline
```

Commit order matters: `dvc push` **before** `git push`.

### 7. Reproduce twice locally, then have Nimra reproduce on a fresh clone

Local determinism check first:

```bash
uv run dvc repro --force
Get-Content metrics.json
uv run dvc repro --force
Get-Content metrics.json
```

Both runs must be identical, byte for byte.

Then Nimra, in a **new folder**:

```bash
git clone --branch feat/dvc-pipeline https://github.com/<esha>/cooked-ml-collab.git repro-check
cd repro-check
uv sync
uv run dvc remote modify storage --local auth <nimra-dagshub-token>
uv run dvc pull
uv run dvc repro
Get-Content metrics.json
```

Her `metrics.json` must match Esha's byte for byte (after removing any timestamp field). Paste both
into the PR. **This is the graded checkpoint** — do not skip the fresh-clone step and do not skip
pasting the output.

### 8. PR

`feat/dvc-pipeline → dev`. Nimra reviews. Since this PR touches `src/` and `dvc.yaml`, she must
check out the branch and run it at least once. Merge (squash), delete the branch.

## Checkpoint evidence

- [x] `params.yaml`, `dvc.yaml`, `dvc.lock`, `metrics.json` committed
- [x] Two consecutive `dvc repro --force` runs produce identical `metrics.json`
- [x] Fresh-clone reproduction matches, output pasted in the PR
- [x] `commit_sha` in `metrics.json` equals `git rev-parse HEAD` of the commit
- [x] Test proves the scaler was fit on training rows only
- [x] No `models/*.joblib` or `data/processed/*` in `git ls-files`
- [x] PR merged, branch deleted

## Gotchas

- **Leakage is the number one thing the reviewer looks for.** Never call `.fit()` on anything
  that touched `test`.
- Listing `params.yaml` in every stage's `deps` means a param change re-runs the whole pipeline —
  that is what makes `dvc exp` in Module 07 work.
- `uv run` inside `dvc.yaml` means DVC must be invoked through uv too (`uv run dvc repro`), or
  `uv` may not be on DVC's PATH. Alternative: use plain `python -m cooked_ml.cli prepare` and run
  everything from an activated environment.
- `dvc repro` needs the raw CSV present; on a fresh clone do `dvc pull` first.
- If DVC reports "output already exists in the workspace and is not tracked", remove the stray
  file before re-running.
