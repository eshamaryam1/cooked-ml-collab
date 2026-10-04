# Progress tracker

Tick a box only when the checkpoint in that module is actually demonstrated in the repo.
Update the tables as you go — this file is the running log the two of us read before every PR.

**Overall status: 5 / 9 modules complete**

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
  - [x] Default branch switched from `chore/check-push-esha` to `main` — done 2026-10-04 by Esha
    (repo admin) with `gh repo edit eshamaryam1/cooked-ml-collab --default-branch main`;
    `origin/HEAD` now resolves to `origin/main` instead of `origin/chore/check-push-esha`
    (not part of Module 02, but flagged while doing step 7)
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
- [x] **M05 — Notebooks** (Esha) — started: 2026-10-03 · done: 2026-10-03
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
  - [x] PR `feat/eda-notebook → dev` opened — [PR #5](https://github.com/eshamaryam1/cooked-ml-collab/pull/5),
    `0 0` outputs check pasted in the body
  - [x] Nimra reviewed (restart kernel, run all cells, no outputs in the diff), approved; squash
    merged — [PR #5](https://github.com/eshamaryam1/cooked-ml-collab/pull/5) → squash `fb2b61e`,
    branch `feat/eda-notebook` deleted from origin
- [x] **M06 — Reproducible pipeline** (Esha) — started: 2026-10-03 · done: 2026-10-03
  - [x] Branch `feat/dvc-pipeline` from `dev`; `uv run dvc pull` before starting
  - [x] `params.yaml` keeps the Module 02 schema — the module doc's `data.raw` / `split` /
    `preprocess` / `train` layout would have broken the merged notebook and ~35 tests; added
    `data.processed_dir` + `data.drop_duplicates` instead (deviation recorded like Module 03)
  - [x] `configs/smoke.yaml` mirrors it with `processed_dir: data/processed_smoke` and
    `max_rows: 500`, so a smoke run can never overwrite the real pipeline's outputs
  - [x] `set_global_seed()` in `src/cooked_ml/config.py` called first by all three stages;
    `PYTHONHASHSEED` set next to `random.seed`/`np.random.seed`, `random_state=seed` on
    `train_test_split` and `RandomForestRegressor`, `n_jobs: 1` in `params.yaml`
  - [x] Stage split in `src/cooked_ml/cli.py` — `prepare` (load → optional dedupe → seeded split
    → `data/processed/{train,test}.csv`), `train` (fit the sklearn `Pipeline` on the processed
    training split → `models/model.joblib`), `evaluate` (`metrics.json`); wired in `dvc.yaml`
  - [x] Leakage fix held: the preprocessor is fitted inside `Pipeline.fit` on
    `data/processed/train.csv` only — `test_scaler_is_fit_on_training_rows_only` asserts the
    scaler's means equal the training means and differ from the whole-frame means
  - [x] `metrics.json`: r2, MAE, `n_train`/`n_test`, seed, `commit_sha` (`git rev-parse HEAD`),
    the params used, the raw CSV sha256 and its `.dvc` pointer md5 — fixed key order, no
    timestamp. `dvc_lock_md5` from the doc's example dropped: `dvc.lock` is rewritten by the
    stage that would hash it, so it changed on every run (3 forced runs differed only in that
    field before it was removed)
  - [x] Two consecutive `uv run dvc repro --force` at commit `b3bf3bc` → byte-identical
    `metrics.json`, sha256 `4C95763D23BFF2937AB8EED5F037224566E1F3A4E47251830AFFBF26CDDE9DAC`
    (`commit_sha` in the file equals `git rev-parse HEAD` of that commit)
  - [x] Shipped metrics **r2 0.7913, MAE 0.3454**. Hyperparameters deviate from the doc's
    `max_depth: 6`, which measures 0.6801 / 0.4604 (the doc's example `r2 0.8157` is not
    reachable there); `n_estimators: 100`, `max_depth: 12` keeps the artefact at 23.4 MB —
    the Module 02 forest was 289 MB and could not be pushed
  - [x] `uv run dvc push` → "3 files pushed"; `uv run dvc status -c` → "Cache and remote
    'storage' are in sync"
  - [x] `uv run pytest tests/ -q` → 41 passed; `ruff check .` + `ruff format --check .` clean;
    `uv run pre-commit run --all-files` green (detect-secrets now excludes the generated
    `metrics.json`, whose hex strings are content hashes)
  - [x] Nimra on a fresh clone: `git clone` → `git checkout b3bf3bc` → `uv sync` → `dvc pull` →
    `dvc repro --force` → identical `metrics.json`, hash pasted into
    [PR #6](https://github.com/eshamaryam1/cooked-ml-collab/pull/6#issuecomment-5970244357) —
    **the graded checkpoint**, 2026-10-03 (Esha's run and Nimra's run:
    `4C95763D23BFF2937AB8EED5F037224566E1F3A4E47251830AFFBF26CDDE9DAC`; git blob
    `dfab793c82186fd6a9bd342fa7e347ca9854afd4` both sides)
  - [x] PR `feat/dvc-pipeline → dev` opened with the checkpoint evidence and the deviations
    listed — [PR #6](https://github.com/eshamaryam1/cooked-ml-collab/pull/6), review requested
    from Nimra
  - [x] Nimra reviewed (diff checked out, 41 tests + `ruff` run on the branch, fresh-clone
    reproduction matched), approved; squash merge — [PR #6](https://github.com/eshamaryam1/cooked-ml-collab/pull/6)
    → squash `1622d4d`, branch `feat/dvc-pipeline` deleted from origin
- [ ] **M07 — Experiments & PRs** (both) — started: 2026-10-03 · done: —
- [ ] **M08 — CI** (Nimra) — started: — · done: —
- [ ] **M09 — Release & report** (both) — started: — · done: —

## Assignment checkpoints

| Phase | Checkpoint | Verified by | Date | Status |
|---|---|---|---|---|
| 1 | All members can push a branch | — | 2026-09-30 | ☑ (`87d044c` Esha, `880bed7` Nimra) |
| 2 | 3 protected branches exist; `git log` on `main` shows the initial import | Esha | 2026-10-01 | ☑ (import on `main`; rules on `main`/`staging`/`dev`, direct push to `dev` rejected GH006) |
| 3 | 5 MB file and a fake API key are both blocked (screenshot) | Nimra | 2026-10-01 | ☑ (`big_blob.bin` 5120 KB refused; detect-secrets refused fake keys — logs + PNG screenshots in `docs/evidence/`) |
| 4 | CSV is not in Git history, only its `.dvc` pointer | Esha | 2026-10-03 | ☑ (`git log --all` and `rev-list --objects --all` both empty; `docs/evidence/04-dvc-no-csv-history.png`) |
| 5 | PR diff shows no cell outputs or execution counts | Nimra | 2026-10-03 | ☑ (Nimra approved PR #5; squash `fb2b61e` — notebook merged with `outputs=0`/`execution_count=0`) |
| 6 | Teammate on a fresh clone: `dvc pull && dvc repro` gives identical metrics | Nimra | 2026-10-03 | ☑ (fresh clone at `b3bf3bc`; SHA256 `4C95763D…CDDE9DAC` identical to Esha's, pasted in [PR #6 comment](https://github.com/eshamaryam1/cooked-ml-collab/pull/6#issuecomment-5970244357)) |
| 7 | Every member is both author and reviewer; ≥1 "changes requested" review | both | 2026-10-04 | ☑ (authored merged: Esha #1/#5/#6/#8/#10/#14, Nimra #2/#3/#4/#7/#9/#12/#13/#15; each has reviewed the other's PRs; "Changes requested" by Esha on [PR #11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11)) |
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
| 5 | feat: add stripped eda notebook paired with jupytext script | Esha | Nimra (approved) | dev | merged (squash `fb2b61e`) — [PR #5](https://github.com/eshamaryam1/cooked-ml-collab/pull/5) | `notebooks/01-eda.ipynb` + `.py`, outputs/execution counts check `0 0` |
| 6 | feat: add seeded dvc pipeline producing reproducible metrics | Esha | Nimra (approved) | dev | merged (squash `1622d4d`) — [PR #6](https://github.com/eshamaryam1/cooked-ml-collab/pull/6) | byte-identical `metrics.json` (`4C95763D…`) confirmed by Nimra on a fresh clone ([comment](https://github.com/eshamaryam1/cooked-ml-collab/pull/6#issuecomment-5970244357)), leakage test, deviations in the body |
| 7 | docs: record module 06 fresh-clone reproduction and close the module | Nimra | Esha (approved) | dev | merged (squash `6ffe5bb`) — [PR #7](https://github.com/eshamaryam1/cooked-ml-collab/pull/7) | Module 06 close-out: fresh-clone checkpoint recorded, `PROGRESS.md` M06 → done (5/9) |
| 8 | fix: ignore model params the selected estimator does not accept | Esha | Nimra (approved) | dev | merged (squash `74eb14e`) — [PR #8](https://github.com/eshamaryam1/cooked-ml-collab/pull/8) | checked out and ran: 45 tests, `ruff` clean, all three model families build from the shared `model.params` block, typo key still rejected |
| 9 | docs: mark module 06 complete in the status table | Nimra | Esha (approved) | dev | merged (squash `9801ce0`) — [PR #9](https://github.com/eshamaryam1/cooked-ml-collab/pull/9) | `docs/README.md` Module 06 → Complete; PR-log row 7 |
| 10 | feat: promote gradient boosting with r2 0.81331 from exp-esha-gbr | Esha | Nimra (approved) | dev | merged (squash `054f9a6`) — [PR #10](https://github.com/eshamaryam1/cooked-ml-collab/pull/10) | reopened, retargeted to `dev` and rebased (duplicated `#8` fix dropped), CRLF `dvc.lock` entry re-recorded as `cf49b73d…`, Nimra's three rows added; provenance `ca24fb7` = `gradient_boosting`, 45 tests + `ruff` clean |
| 11 | data: re-export raw csv with 5 duplicate rows so dedupe has a real effect | Nimra | Esha (**changes requested** 2026-10-04 → **both items fixed & verified**) | dev | open — [PR #11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11) | data v1 → v2 (`b2a3a690…` → `8a862f33…`), 20,640 → 20,645 rows, metrics unchanged; both review items (v1/v2 verify snippet, dirty `dvc status` on a default Windows clone) were fixed by Nimra in [PR #15](https://github.com/eshamaryam1/cooked-ml-collab/pull/15) and Esha verified them on #11; branch is now **conflicting with `dev`** after #14 and #13 (`params.yaml`, `dvc.lock`, `metrics.json`) — one rebase left, then re-approve + merge |
| 12 | docs: log module 07 prs, the abandoned exp branch and the data-update checkpoint | Nimra | Esha (approved) | dev | merged (squash `a0ccd91`) — [PR #12](https://github.com/eshamaryam1/cooked-ml-collab/pull/12) | tracker-only: PR-log rows 8–11, `M07 started: 2026-10-03`, `exp/nimra-ldm` drift slot, data-update box ticked, `docs/README.md` M07 → In progress |
| 13 | feat: raise n_estimators to 200 (Module 07 step 5 — conflict resolved with Esha's max_depth 8) | Nimra | Esha (approved — ran it on the branch) | dev | merged (squash `2bf697b`) — [PR #13](https://github.com/eshamaryam1/cooked-ml-collab/pull/13) | Step 5 second half: rebased onto `4906d30` (#14), `params.yaml` conflict **resolved on camera keeping both intents** (`max_depth: 8` + `n_estimators: 200`), r2 0.81331 → 0.83584 (#14) → **0.84156**, mae 0.29484, artifact 4,924,090 bytes; Esha approved after checking it out — 45 tests, `ruff` clean, `dvc pull` + `dvc status -c` in sync, `dvc repro` skips all three stages, clean tree |
| 14 | feat: raise model max depth to 8 (Module 07 step 5 — Esha's half, merge before #13) | Esha | Nimra (approved) | dev | merged (squash `4906d30`) — [PR #14](https://github.com/eshamaryam1/cooked-ml-collab/pull/14) | conflict-pair first half: `model.params.max_depth: 12 → 8`, r2 **0.81331 → 0.83584**, mae 0.31727 → 0.30230, artifact 18.2 MB → 2.78 MB, byte-identical `metrics.json` over two forced runs |
| 15 | chore: force lf line endings with .gitattributes and fix the v1/v2 verify snippet | Nimra | Esha (approved) | dev | merged (squash `1893642`) — [PR #15](https://github.com/eshamaryam1/cooked-ml-collab/pull/15) | **the fix PR for both changes-requested items on [#11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11)**: `* text=auto eol=lf` + `git add --renormalize .` so `dvc status` stays clean under `core.autocrlf=true` (with the mandatory `git rm --cached -r . ; git reset --hard` refresh), and Step 4's v1 ref fixed `HEAD~1` → `origin/dev`/`HEAD~2`; Esha verified both end-to-end before merging |

Required PRs to link in `REPORT.md`:

- [x] Data update PR (`data/<change>`) — [PR #11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11)
- [x] Conflict resolution PR — [PR #13](https://github.com/eshamaryam1/cooked-ml-collab/pull/13):
  rebased onto #14, `params.yaml` conflict resolved keeping both intents, conflict output and
  rationale in the body, Esha approved after running it → squash `2bf697b`
- [x] A review with "Changes requested" — Esha on [PR #11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11),
  2026-10-04; both items fixed by Nimra in [PR #15](https://github.com/eshamaryam1/cooked-ml-collab/pull/15)
  and verified by Esha on #11
- [ ] Release PR `dev → staging` (titled `release: v1.0`)
- [ ] Release PR `staging → main`
- [ ] One `exp/` branch that was abandoned

## Experiment log

Requirement: **3 experiments per member** (`dvc exp run`), compared with `dvc exp show`.

| Experiment | Member | Branch | Params change | r2 | MAE | Notes |
|---|---|---|---|---|---|---|
| exp-esha-d10 | Esha | `exp/esha-max-depth` | `model.params.max_depth: 12 → 10` | 0.77423 | 0.36595 | Shallower forest loses to base — real result, kept in the table |
| exp-esha-d4 | Esha | `exp/esha-max-depth` | `model.params.max_depth: 12 → 4` | 0.59796 | 0.53151 | Depth collapse; honest negative result |
| exp-esha-gbr | Esha | `exp/esha-max-depth` | `model.name: random_forest → gradient_boosting` | 0.81331 | 0.31727 | Best of the four rows so far; needs [PR #8](https://github.com/eshamaryam1/cooked-ml-collab/pull/8) to train at all |
| exp-nimra-d8 | Nimra | `exp/nimra-d8` | `model.params.max_depth: 12 → 8` | 0.73921 | 0.40181 | Shallow forest loses to base, same shape as Esha's d10/d4 |
| exp-nimra-n300 | Nimra | `exp/nimra-n300` | `model.params.n_estimators: 100 → 300` | 0.79408 | 0.34356 | More trees help a little, still behind gbr — best Nimra row |
| exp-nimra-ldm | Nimra | `exp/nimra-ldm` | `model.name: random_forest → linear_regression` | 0.57579 | 0.53320 | Worst of the seven; branch kept unmerged as the abandoned-experiment evidence |

All three Esha runs at base `216f492` (= `e06970d` of [PR #8](https://github.com/eshamaryam1/cooked-ml-collab/pull/8),
cherry-picked onto the exp branch); `exp/esha-max-depth` is pushed as evidence and never merged.

Nimra's three ran at base `6ffe5bb` / `74eb14e`, seed 42
(`exp/nimra-d8`, `exp/nimra-n300`, `exp/nimra-ldm`). Seven-row order by r2:
gbr **0.81331** > n300 0.79408 > base 0.79133 > d10 0.77423 > d8 0.73921 > d4 0.59796 >
ldm 0.57579 — `exp-esha-gbr` still wins, so no re-promotion is needed.

Winner promoted via `dvc exp apply`: `exp-esha-gbr` (gradient_boosting, r2 0.81331) —
[PR #10](https://github.com/eshamaryam1/cooked-ml-collab/pull/10)

**Shipped config superseded 2026-10-04** by [PR #14](https://github.com/eshamaryam1/cooked-ml-collab/pull/14)
(Module 07 Step 5, Esha's half): `model.params.max_depth: 12 → 8` on the promoted booster →
**r2 0.83584 / MAE 0.30230**, artifact 18,169,722 → 2,775,978 bytes, byte-identical `metrics.json`
(md5 `DC99F32E…`) over two consecutive `dvc repro --force`, then again by
[PR #13](https://github.com/eshamaryam1/cooked-ml-collab/pull/13) (merged squash `2bf697b`),
which rebased into #14's conflict and kept both intents (`max_depth: 8` + `n_estimators: 200`).
**Shipped on `dev` now: `gradient_boosting`, `n_estimators: 200`, `max_depth: 8` →
r2 0.8415635827935704 / MAE 0.294844375210418**, artifact 4,924,090 bytes
(`6b47afe7…`), data still v1 (`b2a3a690…`) until [PR #11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11)
merges. The experiment rows above stay as recorded — they are historical runs, not the shipped
configuration.

## Experiment drift

- [ ] At least one `exp/` branch kept unmerged and explained in `REPORT.md` (branch: `exp/nimra-ldm`)
  - Pushed to origin as evidence and **never merged**: linear regression on the same split scores
    r2 **0.57579** / mae **0.53320** against the promoted model's 0.81331 / 0.31727
    (`exp-esha-gbr`, [PR #10](https://github.com/eshamaryam1/cooked-ml-collab/pull/10)) — and
    against 0.84156 / 0.29484 for what `dev` ships after [#13](https://github.com/eshamaryam1/cooked-ml-collab/pull/13)
    — an honest negative result. Promoting it would have cost ~0.27 r2, which is why it stays
    abandoned. The written explanation lands in `REPORT.md` when Module 09 opens it (box stays
    unticked until then).

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
