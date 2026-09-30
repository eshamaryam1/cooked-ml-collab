# Progress tracker

Tick a box only when the checkpoint in that module is actually demonstrated in the repo.
Update the tables as you go — this file is the running log the two of us read before every PR.

**Overall status: 0 / 9 modules complete**

---

## Modules

- [ ] **M01 — Team & repo setup** (both) — started: 2026-09-29 · done: —
  - [x] Repo created (public, empty) — `eshamaryam1/cooked-ml-collab`
  - [x] Esha's local `user.name` / `user.email` set
  - [x] Nimra added as collaborator (Write) — accepted, `push=true`
  - [ ] Instructor added as viewer — username not known yet
  - [x] Esha proved she can push — branch `chore/check-push-esha`, commit `87d044c`
  - [x] Nimra's clone created and her identity configured — commit `880bed7` authored by
    `Nimra-Saleem29 <ns5999424@gmail.com>` on `chore/check-push-nimra`
  - [x] Nimra proved she can push — branch `chore/check-push-nimra`, commit `880bed7`
- [ ] **M02 — Scaffold & initial import** (both) — started: 2026-09-30 · done: —
  - [x] `uv` 0.12.21 + CPython 3.12.14 installed (pins in `.python-version`)
  - [x] `pyproject.toml` + `uv.lock` committed and pushed — `d15f8a8`
  - [x] `src/cooked_ml/` refactor: `config`, `data`, `features`, `models`, `cli`
  - [x] Deterministic raw CSV written — 20,640 × 9, sha256 `05817eef…d9bb456`,
    `git hash-object 8edefff052981e57ff00439301b7776d3ff93998`
  - [x] Rewriting the CSV from the sklearn cache reproduces byte-identical output
  - [x] Baseline `random_forest`, seed 42, 20% test split: **r2 0.8074, MAE 0.3259**
  - [x] `tests/` — 31 tests passing, `ruff check` + `ruff format --check` clean
  - [x] Nimra: `uv sync` then `.gitignore`, `CONTRIBUTING.md`, `README.md`, PR template —
    committed `chore: add gitignore…`, `docs: add contributing guide and pr template`
  - [x] **Hard gate** — Nimra's `git hash-object data/raw/california_housing.csv` must equal
    `8edefff052981e57ff00439301b7776d3ff93998` before DVC init in Module 04
    — verified on Nimra's clone 2026-09-30: `8edefff052981e57ff00439301b7776d3ff93998`,
    sha256 `05817eef1b24d07428073579db624db1eeccda974211a026c26d6900dd9bb456`, matches Esha
  - [x] `staging` + `dev` created from `main` and pushed — Esha, step 6 — all three branches
    point at the same commit
  - [ ] Branch protection on `main`, `staging`, `dev` — Nimra, step 7 (GitHub → Settings →
    Branches, after step 6 lands)
- [ ] **M03 — pre-commit & secrets** (Nimra) — started: — · done: —
- [ ] **M04 — DVC data versioning** (Nimra) — started: — · done: —
- [ ] **M05 — Notebooks** (Esha) — started: — · done: —
- [ ] **M06 — Reproducible pipeline** (Esha) — started: — · done: —
- [ ] **M07 — Experiments & PRs** (both) — started: — · done: —
- [ ] **M08 — CI** (Nimra) — started: — · done: —
- [ ] **M09 — Release & report** (both) — started: — · done: —

## Assignment checkpoints

| Phase | Checkpoint | Verified by | Date | Status |
|---|---|---|---|---|
| 1 | All members can push a branch | — | 2026-09-30 | ☑ (`87d044c` Esha, `880bed7` Nimra) |
| 2 | 3 protected branches exist; `git log` on `main` shows the initial import | — | — | ☐ (Esha's import is on `main`; branches + protection pending) |
| 3 | 5 MB file and a fake API key are both blocked (screenshot) | — | — | ☐ |
| 4 | CSV is not in Git history, only its `.dvc` pointer | — | — | ☐ |
| 5 | PR diff shows no cell outputs or execution counts | — | — | ☐ |
| 6 | Teammate on a fresh clone: `dvc pull && dvc repro` gives identical metrics | — | — | ☐ |
| 7 | Every member is both author and reviewer; ≥1 "changes requested" review | — | — | ☐ |
| 8 | A deliberately broken test causes a red check that blocks merging | — | — | ☐ |
| 9 | `model-v1.0` exists on `main` and the independent reproduction matched | — | — | ☐ |

## Pull request log

Requirement: **2 authored + 2 reviewed per member**, at least one review with
*"Changes requested"*, plus the specific PRs the report must link.

| # | Title | Author | Reviewer | Target | Outcome | Evidence note |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |
| 7 | | | | | | |
| 8 | | | | | | |

Required PRs to link in `REPORT.md`:

- [ ] Data update PR (`data/<change>`)
- [ ] Conflict resolution PR
- [ ] A review with "Changes requested"
- [ ] Release PR `dev → staging` (titled `release: v1.0`)
- [ ] Release PR `staging → main`
- [ ] One `exp/` branch that was abandoned

## Experiment log

Requirement: **3 experiments per member** (`dvc exp run`), compared with `dvc exp show`.

| Experiment | Member | Branch | Params change | r2 | MAE | Notes |
|---|---|---|---|---|---|---|
| exp001 | | | | | | |
| exp002 | | | | | | |
| exp003 | | | | | | |
| exp004 | | | | | | |
| exp005 | | | | | | |
| exp006 | | | | | | |

Winner promoted via `dvc exp apply`: ______ (PR link: ______)

## Experiment drift

- [ ] At least one `exp/` branch kept unmerged and explained in `REPORT.md` (branch: ______)

## Screenshots needed for `REPORT.md`

- [ ] Pre-commit blocking a 5 MB file
- [ ] Pre-commit / secret scanner blocking a fake API key
- [ ] A failing CI check (red) that blocks the merge
- [ ] A passing CI check (green)

## CI checks (required status checks once Module 08 lands)

- [ ] `lint` — `ruff check` + `ruff format --check`
- [ ] `test` — `pytest tests/`
- [ ] `data-check` — schema, ranges, null counts
- [ ] `smoke-train` — end-to-end on a few hundred rows
- [ ] Bonus: CML metrics comment on PRs (+5)

## Reproducibility record for the released model

Fill this in from `metrics.json` on `main` at tag `model-v1.0`.

| Field | Value |
|---|---|
| Commit SHA | |
| `params.yaml` values | |
| Data `.dvc` hash (`md5` of the raw CSV) | |
| `dvc.lock` | |
| Seed | |
| Final metrics (r2, MAE) | |
| Independent reproduction metrics (member: ) | |
