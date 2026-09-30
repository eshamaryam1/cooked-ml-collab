# Module 08 — CI on every pull request

**Owner:** Nimra (Platform owner), reviewed by Esha
**Depends on:** Module 03 (ruff config), Module 06 (pipeline exists)
**Branch:** `feat/ci` → PR into `dev`
**Checkpoint:** a deliberately broken test causes a red check that blocks merging

---

## Goal

One GitHub Actions workflow that runs on every PR into `dev`, `staging` and `main` and performs
lint, unit tests, data checks and a smoke train — then made required by branch protection.

## Steps

### 1. Branch

```bash
git switch dev
git pull --ff-only
git switch -c feat/ci
```

### 2. Commit a small data sample for the data checks

CI should not need DagsHub credentials for a fast lint/test signal, so commit a small real sample
(well under the 1 MB pre-commit limit):

```bash
uv run python -c "import pandas as pd; d=pd.read_csv('data/raw/california_housing.csv', nrows=200); d.to_csv('tests/fixtures/sample.csv', index=False)"
```

200 rows ≈ 24 KB. Add to `.gitignore` exceptions:

```gitignore
!tests/fixtures/sample.csv
```

The full dataset is still DVC-tracked; the sample exists purely so `data-check` and `smoke-train`
can run in CI with no secrets.

### 3. Data check script

`scripts/check_data.py`, runnable locally and in CI:

```python
from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

FEATURES = [
    "MedInc",
    "HouseAge",
    "AveRooms",
    "AveBedrms",
    "Population",
    "AveOccup",
    "Latitude",
    "Longitude",
]
TARGET = "MedHouseVal"
RANGES: dict[str, tuple[float, float]] = {
    "MedInc": (0.0, 15.01),
    "HouseAge": (0.0, 53.0),
    "AveRooms": (0.0, 100.0),
    "AveBedrms": (0.0, 20.0),
    "Population": (0.0, 35000.0),
    "AveOccup": (0.0, 20.0),
    "Latitude": (32.5, 42.0),
    "Longitude": (-124.5, -114.3),
    "MedHouseVal": (0.0, 6.0),
}
MAX_NULLS = 0


def check(path: str) -> list[str]:
    errors: list[str] = []
    df = pd.read_csv(path)

    missing_cols = [c for c in [*FEATURES, TARGET] if c not in df.columns]
    if missing_cols:
        return [f"missing columns: {missing_cols}"]

    extra_cols = [c for c in df.columns if c not in [*FEATURES, TARGET]]
    if extra_cols:
        errors.append(f"unexpected columns: {extra_cols}")

    for col in [*FEATURES, TARGET]:
        nulls = int(df[col].isna().sum())
        if nulls > MAX_NULLS:
            errors.append(f"{col}: {nulls} nulls (max {MAX_NULLS})")

    for col, (lo, hi) in RANGES.items():
        values = df[col].to_numpy()
        if not np.isfinite(values).all():
            errors.append(f"{col}: contains non-finite values")
        if values.min() < lo or values.max() > hi:
            errors.append(
                f"{col}: values outside [{lo}, {hi}] (got {values.min()}, {values.max()})"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="tests/fixtures/sample.csv")
    args = parser.parse_args()

    errors = check(args.data)
    if errors:
        for error in errors:
            print(f"data-check: {error}", file=sys.stderr)
        return 1

    print(f"data-check: ok ({args.data})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Run it locally:

```bash
uv run python scripts/check_data.py
uv run python scripts/check_data.py --data data/raw/california_housing.csv
```

### 4. Smoke train

Add `data.smoke_rows` support to the CLI: when set, load only the first N rows of the raw CSV and
train on that. `configs/smoke.yaml` (written in Module 06) sets `smoke_rows: 500` and
`n_estimators: 20`.

```bash
uv run python -m cooked_ml.cli repro --config configs/smoke.yaml
```

Verify it runs end to end in well under a minute locally before wiring CI.

### 5. `.github/workflows/ci.yml`

```yaml
name: ci

on:
  pull_request:
    branches: [dev, staging, main]
  push:
    branches: [dev, staging, main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - run: uv sync --all-extras --dev
      - name: ruff check
        run: uv run ruff check .
      - name: ruff format check
        run: uv run ruff format --check .

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - run: uv sync --all-extras --dev
      - name: pytest
        run: uv run pytest tests/ -q

  data-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - run: uv sync --all-extras --dev
      - name: schema, ranges and null counts
        run: uv run python scripts/check_data.py

  smoke-train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - run: uv sync --all-extras --dev
      - name: train end to end on a small sample
        run: uv run python -m cooked_ml.cli repro --config configs/smoke.yaml

  report:
    needs: [lint, test, data-check, smoke-train]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: summary
        run: echo "CI finished for ${{ github.head_ref }}"
```

Job names become the **required status checks**, and they must match exactly what GitHub shows.

### 6. Bonus: CML metrics comment (+5 marks)

Add a `cml` job and a step inside `smoke-train` that posts the metrics table as a PR comment:

```yaml
      - name: publish metrics comment
        if: github.event_name == 'pull_request'
        run: |
          uv run cml comment publish --publish-always \
            --title "Smoke train metrics" \
            --message "$(cat metrics-smoke.json)" \
            --git-url ${{ github.server_url }}/${{ github.repository }}
```

Install with `uv add --dev cml` (modelled on `mlflow`). If this turns out to be flaky on Windows
or in CI, drop it — the +5 is not worth a red pipeline.

### 7. PR and merge

```bash
git push -u origin feat/ci
```

`feat/ci → dev`. Esha reviews. Merge (squash), delete the branch.

### 8. Make the checks required

For **each** of `main`, `staging`, `dev`: Settings → Branches → edit the rule → **Require status
checks to pass before merging** → select `lint`, `test`, `data-check`, `smoke-train` (plus
`report` if you keep it).

If `report` has `if: always()`, it still reports success when jobs pass, so requiring it is fine.
Keep the required list to the four real checks to reduce noise.

### 9. Demonstrate the red check (graded evidence)

On a throwaway branch, break a test and open a PR:

```bash
git switch dev
git switch -c chore/demo-red-ci
```

Edit `tests/test_models.py` to assert something false:

```python
def test_demo_broken():
    from cooked_ml.models import build_model

    assert build_model({"model": "random_forest", "n_estimators": 100, "max_depth": 6}, 42) is None
```

```bash
git push -u origin chore/demo-red-ci
```

Open the PR, wait for the red X, **try to merge it and show the blocked merge message**, then
screenshot both. Save as `docs/evidence/08-ci-failing.png`. Close the PR without merging and
`git branch -D chore/demo-red-ci`.

Then open a clean PR and screenshot the green run as `docs/evidence/08-ci-passing.png`.

## Checkpoint evidence

- [x] `ci.yml` runs on PRs into `dev`, `staging` and `main`
- [x] All four checks green on `dev`
- [x] All four checks are **required** on all three protected branches
- [x] A broken test produced a red check and the merge button was blocked (screenshot)
- [x] A green run screenshotted
- [x] Full CI wall-clock under ~5 minutes

## Gotchas

- `uv sync --all-extras --dev` needs `pyproject.toml` to declare a dev dependency group. If using
  `[dependency-groups]`, `uv sync --group dev` is the right flag.
- DVC must never run in CI — it would need DagsHub credentials. The smoke train runs the CLI
  directly against the committed sample.
- If `data-check` is flaky on the 200-row sample because of min/max range assertions, either widen
  the bounds or use quantile-based assertions. Check the sample's actual extrema before hardcoding.
- GitHub Actions minutes: a public repo is unlimited, a private repo gets 2,000/month on free
  plans. Our pipeline is small, so fine either way.
- Once these are required checks, the **first** PR into `staging`/`main` in Module 09 must wait for
  them to pass. Budget a few minutes.
