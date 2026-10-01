# Module 02 — Scaffold the project and import the initial code

**Owner:** both (Esha writes the pipeline skeleton, Nimra writes the docs/hygiene files)
**Depends on:** Module 01
**Branches:** work happens **directly on `main`** — this is the one and only time the assignment
allows a direct push. Then `staging` and `dev` are created and pushed.
**Checkpoint:** three protected branches exist; `git log` on `main` shows the initial import

---

## Who does what

Module 02 is the only phase where both members push to `main` directly, so the order matters:
**nobody pushes to `main` while someone else is mid-push.** Follow this sequence.

| Step | Who | Blocking? |
|---|---|---|
| 1. Install `uv` + Python 3.12 | both, in parallel | no |
| 2. `uv init --lib --name cooked_ml`, `uv add` deps, commit `pyproject.toml` + `uv.lock`, **push** | Esha | **yes — Nimra waits for this** |
| 3. `uv sync`, then hygiene files (`.gitignore`, `CONTRIBUTING.md`, `README.md`, PR template), generate the raw CSV, **push** | Nimra | yes — Esha waits for this |
| 4. `src/cooked_ml/*` refactor + tests, **push** | Esha | no |
| 5. Compare the raw CSV hash on both machines | both | **yes — hard gate** |
| 6. Create `staging` and `dev`, push | Esha | no |
| 7. Branch protection on all three branches | Nimra | no |

### Nimra's explicit do-not list

- **Do not run `uv init`.** The package name is `cooked_ml` and is decided once, by Esha, in
  step 2. A second `uv init` in another clone creates a conflicting `pyproject.toml`.
- **Do not create or edit anything under `src/`.** That is Esha's.
- **Do not create `staging` or `dev`.** Esha does that in step 6, once `main` is final.
- **Do not push to `main` while Esha is pushing.** Pull first, then push.

---

## Goal

The standard layout in place, the starter code refactored so it runs from the command line with
no hardcoded paths, the environment pinned, and `main` / `staging` / `dev` created and protected.

## Target layout

```
.
├── configs/
│   ├── params.yaml
│   └── smoke.yaml
├── data/
│   ├── raw/
│   └── processed/
├── models/
├── notebooks/
├── scripts/
├── src/
│   └── cooked_ml/
│       ├── __init__.py
│       ├── config.py
│       ├── data.py
│       ├── features.py
│       ├── models.py
│       └── cli.py
├── tests/
│   ├── fixtures/sample.csv
│   ├── test_data.py
│   └── test_models.py
├── docs/
├── .github/
│   ├── workflows/
│   └── pull_request_template.md
├── .gitignore
├── .pre-commit-config.yaml
├── CONTRIBUTING.md
├── README.md
├── REPORT.md
├── params.yaml
└── pyproject.toml
└── uv.lock
```

## Steps

### 1. Environment first

There is currently **no working Python on this machine** (anaconda3 is a half-removed install).
Install `uv`, which manages its own Python, so we never depend on the system one:

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then restart the shell (or use the full path) and:

```bash
uv python install 3.12
uv --version
python --version
```

### 2. Initialise the project

```bash
uv init --lib
uv add pandas scikit-learn joblib pyyaml
uv add --dev pytest ruff ipykernel jupytext
```

Keep `params.yaml` at the repo root (the assignment allows "at the root"), and put the extra
smoke-test variant in `configs/smoke.yaml`. Symlink-free, both are committed.

### 3. `.gitignore`

```gitignore
# env
.venv/
__pycache__/
*.py[cod]
*.egg-info/
.env
.env.*

# data and models are tracked by DVC, never by Git
data/raw/*
data/processed/*
models/*
!data/raw/.gitkeep
!models/.gitkeep

# tooling caches
.dvc/cache/
.ipynb_checkpoints/
.pytest_cache/
.ruff_cache/
mlruns/
wandb/
.DS_Store
```

Leave `*.dvc`, `*.dvc.lock` and `dvc.lock` **not** ignored — those pointers belong in Git.

### 4. Import and refactor the starter code

Source: `mikel-brostrom/Housing_Price_Prediction` (`train.py`, `model.py`, `preprocessing.py`,
`dataloader.py`, `test.py`).

What we take: the California Housing dataset, the three candidate model families reduced to
scikit-learn, and the reporting metrics (`r2`, `MAE`).

What we drop: PyTorch entirely (huge CI install, harder determinism), `tqdm`, the matplotlib
exploration notebook.

What we fix:

| Starter code problem | Our fix |
|---|---|
| `StandardScaler` fit on the whole dataset before `train_test_split` → leakage | Fit the scaler on the **training split only**, inside `src/cooked_ml/features.py` |
| `test_size=0.1`, `random_state=0` hardcoded | Read from `params.yaml`; seed everywhere from `seed: 42` |
| `fetch_california_housing()` called implicitly inside `main()` | Explicit `src/cooked_ml/data.py` that writes a CSV we can DVC-track |
| No CLI, no return codes, prints everything | `python -m cooked_ml.cli train` / `evaluate`, clean `main()` |
| `Preprocessing` class mutating the DataFrame in place | Pure functions that take and return DataFrames |

Resulting module sketch:

```
src/cooked_ml/data.py     -> load_raw(path), build_splits(df, test_size, seed), save_splits(...)
src/cooked_ml/features.py -> make_preprocessor(cfg)   # scaler fitted on train only
src/cooked_ml/models.py   -> build_model(cfg, seed)  # random_forest | linear_regression | gradient_boosting
src/cooked_ml/config.py   -> load_params(path)       # reads params.yaml, no hardcoded values
src/cooked_ml/cli.py      -> argparse entry point
```

Run it:

```bash
uv run python -m cooked_ml.cli train
uv run python -m cooked_ml.cli evaluate
```

Sanity target — the starter repo reports `r2 ≈ 0.81`, `MAE ≈ 0.28` for RandomForest on this
dataset with a 10% test split. With a 20% test split and leakage removed our numbers will move;
record whatever we actually get as the baseline, that is what all later comparisons use.

### 5. Dataset materialisation (needed before DVC, in Module 04)

Write `src/cooked_ml/data.py::ensure_raw_dataset()` that calls
`sklearn.datasets.fetch_california_housing(data_home="data/raw/sklearn_cache")` once and writes a
deterministic CSV to `data/raw/california_housing.csv`.

**Determinism matters** — the DVC hash must be identical on both machines. To guarantee it:

```python
df.to_csv(
    "data/raw/california_housing.csv",
    index=False,
    columns=[*feature_names, "MedHouseVal"],
    float_format="%.10g",
    lineterminator="\n",
)
```

Fixed column order, fixed float format, fixed line terminator. Both members run this once and
compare the file hash before Module 04:

```bash
git hash-object data/raw/california_housing.csv
```

If the two hashes differ, pin `pandas` and `scikit-learn` versions in `uv.lock` and regenerate.
**Do this check before DVC init** — it is much harder to fix afterwards.

Expected shape: 20,640 rows × 9 columns, target `MedHouseVal` (in units of $100,000, range
≈ 0.15 – 5.0). File size ≈ 2.4 MB, which is why the next module's 1 MB large-file hook matters.

### 6. CONTRIBUTING.md

Content from [`PLAYBOOK.md`](PLAYBOOK.md): branch table, branch naming, Conventional Commits,
**our squash-vs-rebase decision** (squash into `dev`, rebase into `staging`/`main`), the PR
checklist, and the review rule that reviewers must actually run the code.

### 7. README.md

Dataset, source link and credit, layout, how to set up (`uv sync`), how to run, how to reproduce
with DVC.

### 8. .github/pull_request_template.md

Verbatim checklist from [`PLAYBOOK.md`](PLAYBOOK.md) — required by Module 07.

### 9. Small, well-described commits on `main`

```
chore: initialise uv project and pin dependencies
chore: add gitignore for data, models and tooling caches
feat: load california housing and write deterministic raw csv
feat: add seeded train/test split with train-only preprocessing
feat: add linear regression and random forest models with CLI
test: cover split determinism and preprocessor fit scope
docs: add contributing guide and pr template
docs: add module plan and progress tracker
```

### 10. Create the long-lived branches and push

```bash
git push -u origin main
git checkout -b staging && git push -u origin staging
git checkout -b dev && git push -u origin dev
```

From here on, nobody pushes to `main`, `staging` or `dev` directly. Ever.

### 11. Branch protection

Do this **before** Module 03, so the first PR already goes through protection. For each of
`main`, `staging`, `dev` — Settings → Branches → Add rule:

| Setting | Value |
|---|---|
| Branch name pattern | `main` / `staging` / `dev` |
| Require a pull request before merging | ✅ |
| Required approvals | 1 |
| Require conversation resolution | ✅ |
| **Do not** allow bypassing the above settings | ✅ |
| Do not allow deletions | ✅ |
| **Do not allow force pushes** | ✅ |

Set the required status checks in Module 08, once the workflow exists.

> **Note:** GitHub only allows `admin` on organization-owned repos, so Nimra could not be given
> admin on this personal repo (the API returns 422). Esha, as owner, applied these rules via
> `PUT /repos/…/branches/{branch}/protection` on 2026-10-01. See `PROGRESS.md`.

## Checkpoint evidence

- [x] `git log main --oneline` shows the initial import
- [x] `git branch -a` shows `main`, `staging`, `dev` on the remote
- [x] Three branch rules exist and a direct `git push origin dev` is rejected
- [x] `git status` is clean; `git ls-files | grep -i csv` shows **no** raw data committed
- [x] Both members' hashes for `data/raw/california_housing.csv` matched

## Gotchas

- `uv init --lib` creates `src/<package>/`; keep that layout, it matches the assignment.
- `data/raw/*` is gitignored but DVC needs the files to exist locally — that is exactly the
  intended arrangement.
- If you let GitHub initialise the repo, delete its README commit before pushing this module.
- Do not create `staging`/`dev` from an older `main` than your latest import; recreate them if
  they are stale (`git branch -D staging && git checkout -b staging main`).
