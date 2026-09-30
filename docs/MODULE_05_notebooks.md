# Module 05 — Notebooks done right

**Owner:** Esha (Model owner), reviewed by Nimra
**Depends on:** Module 04 (the notebook needs `dvc pull`ed data)
**Branch:** `feat/eda-notebook` → PR into `dev`
**Checkpoint:** the PR diff shows no cell outputs or execution counts

---

## Goal

One EDA notebook that diffs and merges cleanly (stripped outputs, paired with a script via
`jupytext`), whose reusable logic lives in `src/` with unit tests rather than in the notebook.

## Steps

### 1. Branch

```bash
git switch dev
git pull --ff-only
git switch -c feat/eda-notebook
uv run dvc pull
```

### 2. Create the notebook

```bash
uv run jupyter nbconvert --to notebook --execute --stdin --stdout > /dev/null 2>&1
uv run python -m jupyter --version
uv run jupyter notebook
```

Create `notebooks/01-eda.ipynb` (Kernel → Python 3.12). Contents, in order:

1. **Setup** — imports, seed, project root resolution, load the raw CSV via
   `src.cooked_ml.data.load_raw("data/raw/california_housing.csv")`.
2. **Shape, dtypes, head** — `d.shape`, `d.dtypes`, `d.head()`.
3. **Missing values** — `d.isna().sum()`.
4. **Summary statistics** — `d.describe()`.
5. **Target distribution** — histogram of `MedHouseVal`.
6. **Feature distributions** — histograms for the 8 features.
7. **Correlations** — `d.corr(numeric_only=True)["MedHouseVal"]` sorted.
8. **Two or three charts** — e.g. `MedInc` vs `MedHouseVal`, `Latitude` vs `Longitude` coloured
   by price.
9. **Observations** — markdown only, written after running.

Rules for this notebook:

- No hardcoded paths. Resolve the repo root once, e.g.
  `ROOT = Path.cwd().parents[1] if Path.cwd().name == "notebooks" else Path.cwd()`.
- Every random operation seeded from `params.yaml`.
- Run it top to bottom from a fresh kernel at least once.

### 3. Pair it with a script via jupytext

```bash
uv run jupytext --set-formats ipynb,py:percent notebooks/01-eda.ipynb
git add notebooks/01-eda.ipynb notebooks/01-eda.py
```

Both files are committed, as the assignment requires. The `.py` twin is excluded from
`nbstripout` in `.pre-commit-config.yaml` (Module 03).

Sync direction matters: edit the `.ipynb` in Jupyter and re-run

```bash
uv run jupytext --sync notebooks/01-eda.ipynb
```

### 4. Promote one reusable function into `src/` with a test

Move one real piece of logic out of the notebook — recommended: **duplicate-row detection and
removal**, or **outlier clipping for `AveOccup` / `Population`**. Pick something the pipeline will
actually use, otherwise Module 06 will just re-inline it.

Example:

```python
# src/cooked_ml/features.py
def drop_duplicate_rows(df: pd.DataFrame, subset: list[str] | None = None) -> pd.DataFrame:
    """Return a copy of df with exact duplicate rows removed."""
    return df.drop_duplicates(subset=subset).reset_index(drop=True)
```

```python
# tests/test_features.py
def test_drop_duplicate_rows_removes_exact_duplicates():
    import pandas as pd
    from cooked_ml.features import drop_duplicate_rows

    df = pd.DataFrame({"a": [1, 1, 2], "b": [3, 3, 4]})
    out = drop_duplicate_rows(df)
    assert len(out) == 2
    assert out.iloc[0].to_dict() == {"a": 1, "b": 3}


def test_drop_duplicate_rows_keeps_input_unchanged():
    import pandas as pd
    from cooked_ml.features import drop_duplicate_rows

    df = pd.DataFrame({"a": [1, 1, 2], "b": [3, 3, 4]})
    before = df.copy()
    drop_duplicate_rows(df)
    pd.testing.assert_frame_equal(df, before)
```

Then import it back into the notebook instead of pasting the code, and re-run all cells.

### 5. Strip outputs before the PR

`nbstripout` does this automatically as a pre-commit hook, so:

```bash
git add -A
git commit -m "feat: add stripped eda notebook paired with jupytext script"
```

The commit hook removes outputs and execution counts from the staged `.ipynb`.

### 6. Verify the diff is clean

```bash
git diff dev...HEAD --stat
uv run python -c "import json;nb=json.load(open('notebooks/01-eda.ipynb'));print(sum(1 for c in nb['cells'] if c.get('outputs')),sum(1 for c in nb['cells'] if c.get('execution_count')))"
```

Expected: `0 0`.

Also confirm `uv run pytest tests/ -q` passes and `uv run ruff check .` is clean.

### 7. PR

```bash
git push -u origin feat/eda-notebook
```

`feat/eda-notebook → dev`. Nimra reviews: restarts the kernel, runs all cells top to bottom, and
confirms the diff has no outputs. Paste that confirmation in the PR. Merge (squash), delete the
branch.

## Checkpoint evidence

- [x] `notebooks/01-eda.ipynb` and `notebooks/01-eda.py` both committed
- [x] `git diff` on the notebook shows no outputs, no execution counts
- [x] Notebook runs top to bottom from a clean kernel on Nimra's machine
- [x] One function promoted to `src/` with at least one unit test in `tests/`
- [x] Notebook imports from `src/`, no duplicated logic
- [x] PR merged, branch deleted

## Gotchas

- Open the notebook from Jupyter with the working directory set to the repo root, otherwise the
  data path breaks on the reviewer's machine. That is exactly the "works on one laptop only"
  mistake the assignment calls out.
- Do not commit a chart image that came from `plt.savefig` — it will bloat the diff. Inline plots
  are fine because `nbstripout` strips them.
- `%matplotlib inline` magic makes the `.py` twin non-runnable with plain `python`. Either add
  `# %matplotlib inline` in percent format or drop the magic and use `display(fig)`.
- If `jupytext` and the `.ipynb` disagree, `jupytext --sync` picks whichever has the newer
  timestamp. Resolve conflicts deliberately rather than letting sync silently overwrite.
