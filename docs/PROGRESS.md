# Progress tracker

Tick a box only when the checkpoint in that module is actually demonstrated in the repo.
Update the tables as you go — this file is the running log the two of us read before every PR.

**Overall status: 1 / 9 modules complete**

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
- [x] **M02 — Scaffold & initial import** (both) — started: 2026-09-30 · done: 2026-10-01
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
  - [x] Branch protection on `main`, `staging`, `dev` — applied 2026-10-01 by Esha (repo
    owner) via the API: PR required (1 approval), conversation resolution, no force pushes, no
    deletions, `enforce_admins` on, no bypass. Direct push to `dev` rejected: `GH006 …
    Changes must be made through a pull request`. Done by Esha instead of Nimra because a
    personal-account repo only has owner + write-collaborator roles — GitHub refuses an
    `admin` collaborator there (422), so Nimra cannot be given admin without moving the repo
    into an org. Status checks to be added in Module 08.
  - [ ] Default branch switched from `chore/check-push-esha` to `main` — repo admin, Settings →
    General (not part of Module 02, but flagged while doing step 7)
- [ ] **M03 — pre-commit & secrets** (Nimra) — started: 2026-10-01 · done: —
  - [x] Branch `feat/pre-commit` from `dev`; `uv add --dev pre-commit detect-secrets` +
    `uv run pre-commit install` (Esha runs the install in her clone too — pending)
  - [x] `.pre-commit-config.yaml` — large files (1 MB cap), merge conflicts, YAML, EOF, trailing
    whitespace, LF line endings, `ruff` + `ruff-format`, `nbstripout`, `detect-secrets`.
    Deviations from the module doc: ruff hook pinned `v0.16.9` to match local ruff 0.16.9
    (doc said `v0.8.4`, which would disagree with CI), nbstripout tag is `0.9.1` (doc said
    `v1.9.1`, which does not exist), gitleaks dropped — its pre-commit hook is
    `language: golang` and no Go toolchain is installed; detect-secrets alone satisfies the
    "such as detect-secrets or gitleaks" requirement
  - [x] `.secrets.baseline` generated with `detect-secrets scan` and committed — only the module
    docs' own demo keys and one placeholder md5
  - [x] Ruff config already in `pyproject.toml` from Module 02 (line-length 100, py312) — no
    change needed, hook and future CI read the same file
  - [x] `uv run pre-commit run --all-files` passes clean — log `docs/evidence/03-precommit-all-files.txt`
  - [x] 5 MB file blocked: `big_blob.bin (5120 KB) exceeds 1024 KB` — log
    `docs/evidence/03-precommit-large-file.txt`
  - [x] Fake API key blocked by detect-secrets (high entropy + keyword + AWS key) — log
    `docs/evidence/03-precommit-secret.txt`
  - [x] PNG screenshots under `docs/evidence/`
  - [ ] PR `feat/pre-commit → dev` reviewed by Esha and merged (squash); branch deleted
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
| 2 | 3 protected branches exist; `git log` on `main` shows the initial import | Esha | 2026-10-01 | ☑ (import on `main`; rules on `main`/`staging`/`dev`, direct push to `dev` rejected GH006) |
| 3 | 5 MB file and a fake API key are both blocked (screenshot) | Nimra | 2026-10-01 | ☑ (`big_blob.bin` 5120 KB refused; detect-secrets refused fake keys — logs + PNG screenshots in `docs/evidence/`) |
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
| 1 | docs: record branch protection and close module 02 | Esha | Nimra (approved) | dev | merged (squash `b117ca1`) | Module 02 close-out, `PROGRESS.md` + `MODULE_02_scaffold.md` |
| 2 | chore: add pre-commit hooks for lint, notebooks, large files and secrets | Nimra | Esha (requested) | dev | open — [PR #2](https://github.com/eshamaryam1/cooked-ml-collab/pull/2) | `docs/evidence/03-precommit-*.txt` |
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
