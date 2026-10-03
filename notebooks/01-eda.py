# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python 3.12
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 01 — Exploratory data analysis
#
# California housing, raw CSV tracked with DVC at `data/raw/california_housing.csv`.
#
# Reusable logic lives in `src/cooked_ml/`; this notebook only calls it. Outputs and
# execution counts are stripped before every commit (`nbstripout`), and the `.py` twin
# is kept in step with `jupytext --sync`.

# %% [markdown]
# ## Setup

# %%
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from cooked_ml.data import TARGET, load_raw
from cooked_ml.features import drop_duplicate_rows

ROOT = next(
    parent for parent in (Path.cwd(), *Path.cwd().parents) if (parent / "params.yaml").is_file()
)
params = yaml.safe_load((ROOT / "params.yaml").read_text(encoding="utf-8"))
SEED = int(params["seed"])
np.random.seed(SEED)

raw_path = ROOT / params["data"]["raw_path"]
d = load_raw(raw_path)
SEED, raw_path.relative_to(ROOT), d.shape

# %% [markdown]
# ## Shape, dtypes and head

# %%
d.shape

# %%
d.dtypes

# %%
d.head()

# %% [markdown]
# ## Missing values

# %%
missing = pd.DataFrame({"nulls": d.isna().sum(), "percent": d.isna().mean().mul(100)})
missing

# %%
d.isna().any().any()

# %% [markdown]
# ## Summary statistics

# %%
d.describe().T

# %% [markdown]
# ## Target distribution

# %%
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(d[TARGET], bins=50, color="steelblue", edgecolor="white")
ax.set(xlabel=TARGET, ylabel="count", title="Distribution of median house value")
mean_target = d[TARGET].mean()
ax.axvline(mean_target, color="crimson", linestyle="--", label=f"mean = {mean_target:.3f}")
ax.legend()
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Feature distributions

# %%
features = [column for column in d.columns if column != TARGET]
fig, axes = plt.subplots(2, 4, figsize=(14, 7))
for column, ax in zip(features, axes.flat, strict=True):
    ax.hist(d[column], bins=50, color="seagreen", edgecolor="white")
    ax.set_title(column)
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Correlations with the target

# %%
correlations = d.corr(numeric_only=True)[TARGET].drop(TARGET).sort_values(ascending=False)
correlations

# %%
fig, ax = plt.subplots(figsize=(7, 4))
correlations.sort_index().plot.bar(ax=ax, color="slateblue", rot=45)
ax.set(ylabel=f"corr with {TARGET}", title="Feature vs target correlation")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Charts

# %%
fig, ax = plt.subplots(figsize=(7, 4))
ax.scatter(d["MedInc"], d[TARGET], s=8, alpha=0.3, color="teal")
ax.set(xlabel="MedInc", ylabel=TARGET, title="Income vs house value")
plt.tight_layout()
plt.show()

# %%
fig, ax = plt.subplots(figsize=(7, 5))
points = ax.scatter(d["Longitude"], d["Latitude"], c=d[TARGET], cmap="viridis", s=6, alpha=0.6)
fig.colorbar(points, ax=ax, label=TARGET)
ax.set(xlabel="Longitude", ylabel="Latitude", title="Where the expensive houses are")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Duplicate rows
#
# The dedup logic is not defined here: `drop_duplicate_rows` lives in
# `src/cooked_ml/features.py` with unit tests in `tests/test_features.py`.
# The pipeline (Module 06) imports the same function.

# %%
d_clean = drop_duplicate_rows(d)
print(f"{len(d)} rows -> {len(d_clean)} rows ({len(d) - len(d_clean)} duplicates removed)")

# %% [markdown]
# ## Observations
#
# - **Shape** — 20,640 rows × 9 columns (8 features + `MedHouseVal`). Every column is numeric:
#   `HouseAge` and `Population` are integers, the rest floats.
# - **No missing values** anywhere, and `load_raw` refuses to hand back a frame that has any,
#   so no imputation decision is needed on the raw file (the `median` strategy in `params.yaml`
#   is a safety net, not a requirement).
# - **Target is right-censored** — mean 2.069, median 1.797, max 5.00001: **992 rows sit
#   exactly on the $500,001 ceiling**. Metrics in Module 06 will be floored by that pile-up.
# - **`MedInc` dominates** — correlation 0.688 with the target, more than four times any other
#   feature. The next strongest are `AveRooms` (0.152) and `HouseAge` (0.106); `Latitude` is the
#   strongest negative (-0.144) because the expensive coastal clusters sit in the north-west.
# - **Heavy right tails** — `AveOccup` (mean 3.07, max 1243), `AveRooms` and `Population` are
#   block-group aggregates with extreme outliers; scaling alone will not fix them, so Module 06
#   should consider clipping or a log transform.
# - **No duplicates** — `drop_duplicate_rows` (imported from `src/cooked_ml/features.py`, tested
#   in `tests/test_features.py`) reports 0 removals, so dedup is a no-op on this snapshot but is
#   ready for future data drops.
# - **Geography is signal** — the map shows price hot spots around the Bay Area and Los
#   Angeles, consistent with `Latitude`/`Longitude` mattering to the tree model.
