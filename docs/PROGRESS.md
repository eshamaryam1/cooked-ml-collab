# Progress tracker

Tick a box only when the checkpoint in that module is actually demonstrated in the repo.
Update the tables as you go — this file is the running log the two of us read before every PR.

**Overall status: 3 / 9 modules complete**

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
- [x] **M03 — pre-commit & secrets** (Nimra) — started: 2026-10-01 · done: 2026-10-03
  - [x] Branch `feat/pre-commit` from `dev`; `uv add --dev pre-commit detect-secrets` +
    `uv run pre-commit install` (Esha's clone installed too — 2026-10-03,
    `pre-commit installed at .git\hooks\pre-commit`)
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
  - [x] PR `feat/pre-commit → dev` reviewed by Esha and merged (squash); branch deleted —
    [PR #2](https://github.com/eshamaryam1/cooked-ml-collab/pull/2) → squash `d32ed2f`,
    [PR #3](https://github.com/eshamaryam1/cooked-ml-collab/pull/3) → squash `58264aa`
    (both approved by Esha; `feat/pre-commit` gone from origin)
- [x] **M04 — DVC data versioning** (Nimra) — started: 2026-10-01 · done: 2026-10-03
  - [x] CSV hash checked: `git hash-object` = `8edefff052981e57ff00439301b7776d3ff93998`
    — confirmed on Esha's fresh clone 2026-10-03: identical
  - [x] Branch `data/initial-dataset`; `uv add "dvc[s3]"` + `uv run dvc init`
  - [x] `data/raw/california_housing.csv.dvc` committed; the CSV is git-ignored by DVC's own
    `data/raw/.gitignore`, `git ls-files` shows only `tests/fixtures/sample.csv`
  - [x] Gotcha found & fixed: Module 02's blanket `data/raw/*` made dulwich (DVC's default git
    backend) prune `data\raw\` during its walk, hiding the `.dvc` pointer from
    `dvc status/push/pull` ("Everything is up to date" while pushing nothing). Replaced with
    DVC-managed per-file ignores — commit `5206509`
  - [x] detect-secrets flagged the pointer's md5 as high entropy — allowlisted with an inline
    `# pragma: allowlist secret` on the `md5:` line (survives `dvc add` rewrites)
  - [x] Remote `storage` = `https://dagshub.com/Nimra-Saleem29/cooked-ml-collab.dvc`; token only
    in gitignored `.dvc/config.local` (`.dvc/config` holds the URL, no credentials)
  - [x] `dvc push` → "1 file pushed"; `dvc status -c` → "Cache and remote 'storage' are in sync"
  - [x] `git log --all -- <csv>` and `git rev-list --objects --all` both empty — screenshot for
    `REPORT.md`
  - [x] Esha fresh-clone `dvc pull` + `(20640, 9)` check pasted in the PR — 2026-10-03,
    [PR #4 comment](https://github.com/eshamaryam1/cooked-ml-collab/pull/4#issuecomment-5967319500)
    (`dvc status -c` in sync, hash `8edefff…998` reproduced in the fresh clone)
  - [x] PR `data/initial-dataset → dev` reviewed, squash-merged; branch deleted —
    [PR #4](https://github.com/eshamaryam1/cooked-ml-collab/pull/4) → squash `b6a2302`,
    approved by Esha; branch gone from origin
- [ ] **M05 — Notebooks** (Esha) — started: 2026-10-03 · done: —
  - [x] Branch `feat/eda-notebook` from `dev`
  - [x] `notebooks/01-eda.ipynb` runs top to bottom from a fresh kernel — executed twice with
    `uv run jupyter nbconvert --to notebook --execute --inplace`; covers setup, shape/dtypes/head,
    missing values, `describe()`, target + feature histograms, correlations, `MedInc` and
    lat/lon charts, and a markdown Observations cell written from the real output
  - [x] No hardcoded paths: repo root resolved by walking up to `params.yaml`; seed 42 and
    `data/raw_path` read from `params.yaml`, not pasted into cells
  - [x] Paired with `notebooks/01-eda.py` (`jupytext --set-formats ipynb,py:percent`);
    `jupytext --sync` reports both files unchanged; the twin runs with plain
    `python notebooks/01-eda.py` (no `%matplotlib inline` magic)
  - [x] `drop_duplicate_rows` promoted to `src/cooked_ml/features.py` with 4 tests in
    `tests/test_features.py`; the notebook imports it instead of inlining the logic
  - [x] `nbstripout` hook strips outputs on commit — `outputs=0, execution_count=0` verified
    with `pre-commit run nbstripout --files notebooks/01-eda.ipynb`
  - [x] `uv run pytest tests/ -q` → 35 passed; `ruff check .` and `ruff format --check .` clean
    (ruff `per-file-ignores` for `notebooks/*.py`: `B018` bare cell expressions, `RUF003`
    notebook prose)
  - [ ] PR `feat/eda-notebook → dev` reviewed by Nimra (restart kernel, run all, confirm no
    outputs in the diff), squash-merged; branch deleted
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
| 4 | CSV is not in Git history, only its `.dvc` pointer | Esha | 2026-10-03 | ☑ (`git log --all` and `rev-list --objects --all` both empty; `docs/evidence/04-dvc-no-csv-history.png`) |
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
| 2 | chore: add pre-commit hooks for lint, notebooks, large files and secrets | Nimra | Esha (approved) | dev | merged (squash `d32ed2f`) — [PR #2](https://github.com/eshamaryam1/cooked-ml-collab/pull/2) | `docs/evidence/03-precommit-*.txt` |
| 3 | chore: add pre-commit hooks for lint, notebooks, large files and secrets | Nimra | Esha (approved) | dev | merged (squash `58264aa`) — [PR #3](https://github.com/eshamaryam1/cooked-ml-collab/pull/3) | `docs/evidence/03-precommit-*.txt` (screenshots PR) |
| 4 | data: track california housing csv with dvc | Nimra | Esha (approved, fresh-clone verified) | dev | merged (squash `b6a2302`) — [PR #4](https://github.com/eshamaryam1/cooked-ml-collab/pull/4) | fresh-clone comment + `docs/evidence/04-dvc-no-csv-history.png` |
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

- [x] Pre-commit blocking a 5 MB file (`docs/evidence/03-precommit-large-file.png`)
- [x] Pre-commit / secret scanner blocking a fake API key (`docs/evidence/03-precommit-secret.png`)
- [x] `git log --all -- data/raw/california_housing.csv` empty — no data in Git history (M04) —
  `docs/evidence/04-dvc-no-csv-history.png`
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
