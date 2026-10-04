# Assignment Modules — Git-Based Collaboration for an ML Project

Working plan for team **cooked** (Esha + Nimra). One file per assignment phase. Each module
lists the owner, the branches to use, the exact steps, and the checkpoint evidence to capture
for `REPORT.md`.

## Team

| Member | GitHub | Role(s) | Owns |
|---|---|---|---|
| Esha | [`@eshamaryam1`](https://github.com/eshamaryam1) | **Model owner** | `params.yaml`, `src/` pipeline, `dvc.yaml`, experiments, notebooks |
| Nimra | [`@Nimra-Saleem29`](https://github.com/Nimra-Saleem29) | **Data owner + Platform owner** | DVC + remote, data checks, data-update PR, pre-commit, CI, releases |

Everyone codes and everyone reviews. Phase 7 requires **2 authored + 2 reviewed PRs per person**.

- Repository: <https://github.com/eshamaryam1/cooked-ml-collab> (public)
- Instructor: added as a viewer once the username is available
- Dataset: California Housing (regression), from
  <https://github.com/mikel-brostrom/Housing_Price_Prediction> (starter code adapted from that repo;
  the underlying data is `sklearn.datasets.fetch_california_housing`)
- Starter code source to credit in `REPORT.md`: `mikel-brostrom/Housing_Price_Prediction`
- Environment: `uv` + committed `uv.lock`
- DVC remote: DagsHub
- Pipeline scope: scikit-learn only (the PyTorch NN from the starter repo is dropped)

## Module order

Do these in order. Each one depends on the previous.

| # | Module | Owner | Status |
|---|---|---|---|
| 1 | [Module 01 — Team & repo setup](MODULE_01_setup.md) | both | In progress — instructor invite outstanding |
| 2 | [Module 02 — Scaffold & initial import](MODULE_02_scaffold.md) | both | Complete |
| 3 | [Module 03 — Guard rails: pre-commit & secrets](MODULE_03_precommit.md) | Nimra | Complete |
| 4 | [Module 04 — Version the data with DVC](MODULE_04_dvc.md) | Nimra | Complete |
| 5 | [Module 05 — Notebooks done right](MODULE_05_notebooks.md) | Esha | Complete |
| 6 | [Module 06 — Reproducible DVC pipeline](MODULE_06_pipeline.md) | Esha | Complete |
| 7 | [Module 07 — Experiments & pull requests](MODULE_07_experiments_prs.md) | both | In progress |
| 8 | [Module 08 — CI on every pull request](MODULE_08_ci.md) | Nimra | Not started |
| 9 | [Module 09 — Release: dev → staging → main](MODULE_09_release.md) | both | Not started |

Progress is tracked in [PROGRESS.md](PROGRESS.md). Shared rules live in
[PLAYBOOK.md](PLAYBOOK.md) — read that before your first PR.

## How to work a module

1. Open the module file and read the **Goal**, **Depends on**, and **Gotchas** sections.
2. Pull the latest `dev`: `git switch dev && git fetch && git merge --ff-only origin/dev`
3. Create the branch the module specifies.
4. Do the work, committing in small Conventional Commit steps.
5. Push the branch, open a PR into `dev`, assign the teammate as reviewer.
6. Reviewer checks out the branch locally and actually runs it (pipeline PRs especially).
7. Merge, delete the branch, tick the boxes in `PROGRESS.md`.

## Things that will bite you

- **`dvc push` before `git push`, every time.** A missing `dvc push` leaves your teammate with a
  broken pointer and they cannot reproduce anything.
- **The raw CSV is ~2.4 MB, so `check-added-large-files` (1 MB limit) will block a plain
  `git add data/raw/*.csv`.** With DVC you only ever stage the `.dvc` pointer plus `data/.gitignore`.
- **Never run `dvc exp` with uncommitted changes.** The commit SHA logged in `metrics.json` must
  match the code that produced it.
- **The starter code leaks data**: it fits the `StandardScaler` on the full dataset before
  `train_test_split`. Module 06 fixes that; do not carry the old `preprocessing.py` forward.
- **Only Phase 2 pushes directly to `main`.** After that everything goes through a reviewed PR.
