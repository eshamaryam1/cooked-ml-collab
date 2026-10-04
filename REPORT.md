# REPORT — cooked-ml-collab

California Housing regression, shipped from `dev → staging → main` with a reviewed PR at every
step, a CI gate on every PR, and an independently reproduced release.

## 1. Team

| Member | GitHub | Roles | Contribution |
|---|---|---|---|
| Esha | [@eshamaryam1](https://github.com/eshamaryam1) | Model owner, repo owner | Owned the modelling line: the EDA notebook ([#5](https://github.com/eshamaryam1/cooked-ml-collab/pull/5)), the seeded DVC pipeline ([#6](https://github.com/eshamaryam1/cooked-ml-collab/pull/6)), the shared-params fix that lets one `model.params` block drive every estimator family ([#8](https://github.com/eshamaryam1/cooked-ml-collab/pull/8)), the gradient-boosting promotion ([#10](https://github.com/eshamaryam1/cooked-ml-collab/pull/10)) and the `max_depth: 12 → 8` half of the conflict pair ([#14](https://github.com/eshamaryam1/cooked-ml-collab/pull/14)). Applied and administers branch protection and the required status checks, requested the one *"changes requested"* review of the project on [#11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11), took over Module 08 when Nimra's machine went down and built the CI workflow ([#19](https://github.com/eshamaryam1/cooked-ml-collab/pull/19)) plus the red-check checkpoint demo ([#20](https://github.com/eshamaryam1/cooked-ml-collab/pull/20)). Reviewed and approved 14 of Nimra's PRs and merged every release PR. |
| Nimra | [@Nimra-Saleem29](https://github.com/Nimra-Saleem29) | Data owner, Platform owner | Owned the platform line: pre-commit + secrets baseline ([#2](https://github.com/eshamaryam1/cooked-ml-collab/pull/2), [#3](https://github.com/eshamaryam1/cooked-ml-collab/pull/3)), DVC tracking of the raw CSV ([#4](https://github.com/eshamaryam1/cooked-ml-collab/pull/4)), the data v1 → v2 re-export with real duplicates ([#11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11)), the tracker/log PRs ([#12](https://github.com/eshamaryam1/cooked-ml-collab/pull/12), [#15](https://github.com/eshamaryam1/cooked-ml-collab/pull/15) and [#18](https://github.com/eshamaryam1/cooked-ml-collab/pull/18)), the conflict-resolution PR ([#13](https://github.com/eshamaryam1/cooked-ml-collab/pull/13)), the whole release train ([#21](https://github.com/eshamaryam1/cooked-ml-collab/pull/21), [#22](https://github.com/eshamaryam1/cooked-ml-collab/pull/22)), the Module 09 hotfix ([#23](https://github.com/eshamaryam1/cooked-ml-collab/pull/23)) and its sync back into `dev` ([#24](https://github.com/eshamaryam1/cooked-ml-collab/pull/24)). Ran the **independent reproduction** of the release from a fresh clone (§3, §5). Reviewed and approved 9 of Esha's PRs, including the CI PR before it merged. |

14 of the 24 PRs are authored by Nimra, 10 by Esha (including the throwaway #20); both members are
author *and* reviewer on the other's work, and Esha's *changes requested* on #11 was worked through
to a verified re-approval.

## 2. Dataset and starter code

- **Dataset:** California Housing (regression) — 20,640 rows × 8 features, target `MedHouseVal`
  (capped at 5.00001, reported as 0–6).
- **Source:** starter code [mikel-brostrom/Housing_Price_Prediction](https://github.com/mikel-brostrom/Housing_Price_Prediction);
  underlying data `sklearn.datasets.fetch_california_housing`.
- **Shipped data (v2):** 20,645 raw rows with 5 deliberate duplicates injected in
  [#11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11) so that `drop_duplicates: true`
  has a real effect → 20,640 rows after dedupe (16,512 train + 4,128 test).
  `md5` of the raw CSV `.dvc` pointer `8a862f33970de79c84a533bf841050cc`, content
  `sha256 130b4a03a5ae54a47acca4a6797203b4da62afadf6349259fab6fb4085c6dc5d`.
- **What we changed from the starter code:**
  - **fixed data leakage** — the starter fitted `StandardScaler` on the whole dataset before the
    split; ours lives inside the sklearn `Pipeline`, fit on training rows only
    (`tests/test_models.py::test_scaler_is_fitted_on_training_split_only`,
    `tests/test_data.py::test_scaler_is_fit_on_training_rows_only`)
  - **seeding everywhere** — `set_global_seed()` sets `PYTHONHASHSEED`, `random` and `numpy`
    before any stage runs; the split uses `random_state=seed`
  - **torch dropped** — the starter's NN was replaced by scikit-learn estimators
    (`random_forest`, `gradient_boosting`, `linear_regression`) selected from `params.yaml`
  - **CLI added** — `python -m cooked_ml.cli {prepare,train,evaluate}`, every value read from
    `params.yaml`, errors reported on stderr with a non-zero exit code
  - **DVC end to end** — raw CSV out of Git (pointer only), `dvc.yaml` pipeline, seeded and
    byte-reproducible `metrics.json`
  - **platform** — `uv`-pinned environment, pre-commit (large files, secrets, ruff, nbstripout,
    LF endings), GitHub Actions CI on every PR

## 3. Reproducibility table for model-v1.0

| Field | Value |
|---|---|
| Tag | `model-v1.0` (annotated; `model-v1.0.1` = hotfix `48c07f2`, no metric change) |
| Commit SHA | `e2449f83cb03c1ca4d232ffc35341a5f3f2be540` (tip of `main` after [#22](https://github.com/eshamaryam1/cooked-ml-collab/pull/22), tree identical to `staging` and `dev`) |
| `params.yaml` values | `seed: 42` · `data: {raw_path: data/raw/california_housing.csv, cache_dir: data/raw/sklearn_cache, processed_dir: data/processed, target: MedHouseVal, test_size: 0.2, drop_duplicates: true, max_rows: null}` · `preprocessing: {scale: true, impute_strategy: median}` · `model: {name: gradient_boosting, params: {max_depth: 8, n_estimators: 200, min_samples_leaf: 1, n_jobs: 1}}` · `artifacts: {model_path: models/model.joblib, metrics_path: metrics.json}` |
| Raw data `.dvc` hash | `8a862f33970de79c84a533bf841050cc` (CSV `sha256 130b4a03…dc5d`, 1,426,634 bytes) |
| `dvc.lock` | file `md5 d18b75f8de2ae6168e7fd42fb2c5085e`; outs: `metrics.json 4360f64b875ac1c087b0c02cb836b052`, `model.joblib 6b47afe735424d126bf46babcc8ff87f`, `train.csv 26a4ba5db29872e0a4d7ba8e830e109d`, `test.csv c9371e937007c2bb8a72705a50ca2525` |
| Seed | 42 (split, estimator `random_state`, `PYTHONHASHSEED`) |
| Final metrics | r2 = **0.8415635827935704**, MAE = **0.294844375210418** (16,512 / 4,128 rows) |
| Independent reproduction (by Nimra) | r2 = **0.8415635827935704**, MAE = **0.294844375210418** — **matches exactly** (only `commit_sha` differs, by design) |

Reproduction detail: fresh clone → `uv sync` → `dvc pull` → `dvc repro --force`; every metric,
count, param and data hash identical, and `dvc.lock`'s model/split outputs reproduced
byte-for-byte. Full transcript, both `metrics.json` files side by side and the whole-tree diff:
[`docs/evidence/09-reproduction.md`](docs/evidence/09-reproduction.md), posted on
[PR #21](https://github.com/eshamaryam1/cooked-ml-collab/pull/21#issuecomment-5983279345).

## 4. Experiments

`uv run dvc exp show -A` comparison — six experiments (three per member), base = the shipped
`random_forest`, `max_depth: 12`:

| Experiment | Member | Branch | Params change | r2 | MAE |
|---|---|---|---|---|---|
| base | — | — | `random_forest`, depth 12, 100 trees | 0.79133 | 0.34542 |
| exp-esha-d10 | Esha | `exp/esha-max-depth` | `max_depth: 12 → 10` | 0.77423 | 0.36595 |
| exp-esha-d4 | Esha | `exp/esha-max-depth` | `max_depth: 12 → 4` | 0.59796 | 0.53151 |
| exp-esha-gbr | Esha | `exp/esha-max-depth` | `model: random_forest → gradient_boosting` | **0.81331** | 0.31727 |
| exp-nimra-d8 | Nimra | `exp/nimra-d8` | `max_depth: 12 → 8` | 0.73921 | 0.40181 |
| exp-nimra-n300 | Nimra | `exp/nimra-n300` | `n_estimators: 100 → 300` | 0.79408 | 0.34356 |
| exp-nimra-ldm | Nimra | `exp/nimra-ldm` | `model: random_forest → linear_regression` | 0.57579 | 0.53320 |

**Why the winner was chosen.** `exp-esha-gbr` beat every other row *and* the base by +0.022 r2 /
−0.028 MAE, while both depth-shrinkage runs and the linear model lost to base — so boosting was
the clear choice and it was promoted with `dvc exp apply` in
[#10](https://github.com/eshamaryam1/cooked-ml-collab/pull/10). Module 07 Step 5 then tuned the
promoted booster on `dev`: `max_depth: 12 → 8` ([#14](https://github.com/eshamaryam1/cooked-ml-collab/pull/14),
r2 → 0.83584, artifact 18.2 MB → 2.78 MB) and `n_estimators: 100 → 200`
([#13](https://github.com/eshamaryam1/cooked-ml-collab/pull/13), the conflict-pair PR), landing at
**r2 0.8415635827935704 / MAE 0.294844375210418** — the released model. The experiment rows stay
as recorded (historical runs on data v1); nothing after #10 re-promoted a different family.

`exp/nimra-ldm` (abandoned, never merged) is explained in §5 and in
[`docs/PROGRESS.md`](docs/PROGRESS.md#experiment-drift).

## 5. Required links

- **Data update PR:** [#11 data: re-export raw csv with 5 duplicate rows so dedupe has a real effect](https://github.com/eshamaryam1/cooked-ml-collab/pull/11) — squash `9c2870d`, data v1 → v2
- **Conflict resolution PR:** [#13 feat: raise n_estimators to 200 (conflict resolved with Esha's max_depth 8)](https://github.com/eshamaryam1/cooked-ml-collab/pull/13) — squash `2bf697b`, `params.yaml` conflict resolved keeping both intents
- **A "changes requested" review:** Esha on [#11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11) (2026-10-04) — both items fixed by Nimra in [#15](https://github.com/eshamaryam1/cooked-ml-collab/pull/15) and verified by Esha on the rebased branch before re-approval
- **Release PR `dev → staging`:** [#21 release: v1.0](https://github.com/eshamaryam1/cooked-ml-collab/pull/21) — rebase-merged to `8e53163`, carries the reproduction comment
- **Release PR `staging → main`:** [#22 release: model-v1.0](https://github.com/eshamaryam1/cooked-ml-collab/pull/22) — rebase-merged to `e2449f8`, tagged `model-v1.0`
- **Abandoned `exp/` branch:** [`exp/nimra-ldm`](https://github.com/eshamaryam1/cooked-ml-collab/tree/exp/nimra-ldm) — pushed as evidence and never merged: linear regression scores r2 0.57579 / MAE 0.53320 against the released 0.84156 / 0.29484. Promoting it would have cost ≈0.27 r2; it stays unmerged as our honest negative result. (`exp/esha-max-depth` likewise stayed unmerged; winners were cherry-picked out of it.)

## 6. Screenshots

| What | File |
|---|---|
| Large file blocked (5 MB refused by the 1 MB hook) | [`docs/evidence/03-precommit-large-file.png`](docs/evidence/03-precommit-large-file.png) (+ `.txt` transcript) |
| Secret blocked (fake API key refused by detect-secrets) | [`docs/evidence/03-precommit-secret.png`](docs/evidence/03-precommit-secret.png) (+ `.txt` transcript) |
| Failing CI that blocks the merge (red) | [`docs/evidence/08-ci-failing.txt`](docs/evidence/08-ci-failing.txt) — transcript of [PR #20](https://github.com/eshamaryam1/cooked-ml-collab/pull/20): `test` FAILED, three jobs green, `gh pr merge` refused, `mergeState=BLOCKED` (the GitHub run URL for the screenshot is inside the file) |
| Passing CI (green) | [`docs/evidence/08-ci-passing.txt`](docs/evidence/08-ci-passing.txt) — all five jobs green in 62 s on [#19](https://github.com/eshamaryam1/cooked-ml-collab/pull/19) (run URL inside) |
| No data in Git history (bonus) | [`docs/evidence/04-dvc-no-csv-history.png`](docs/evidence/04-dvc-no-csv-history.png) |
| Release reproduced from a fresh clone (bonus) | [`docs/evidence/09-reproduction.md`](docs/evidence/09-reproduction.md) |

## 7. Branching and protection

One direction only: `feat/*` → `dev` → `staging` → `main`, every step a reviewed PR;
**squash into `dev`, rebase into `staging`/`main`** ([`docs/PLAYBOOK.md`](docs/PLAYBOOK.md),
[`CONTRIBUTING.md`](CONTRIBUTING.md)).

| Branch | Rule |
|---|---|
| `main` | PR required, 1 approval, `lint`/`test`/`data-check`/`smoke-train` required and green, `enforce_admins` on, no force push / no deletion, conversations resolved; **every merge tagged** |
| `staging` | same rule set |
| `dev` | same rule set |

Live verification any collaborator can run (`gh api .../branches/<b> --jq .protected` → `true`
for all three; direct push to `dev` rejected with `GH006`), the full rule bodies as recorded when
they were applied, and the red-check proof that the required checks really refuse a merge:
[`docs/evidence/09-branch-protection.txt`](docs/evidence/09-branch-protection.txt).

## 8. Retrospective

**What broke (real incidents, in order):**

1. **The 1 MB large-file hook vs the raw CSV.** The CSV is 1,426,634 bytes — over the hook's cap —
   so `git add data/raw/california_housing.csv` was refused in Module 04. It forced the
   pointer-only workflow (`.dvc` file + `.gitignore` rule) we now use everywhere, and it is why CI
   carries its own 200-row sample instead of `dvc pull`-ing in a job.
2. **CRLF churn made `dvc status` permanently dirty.** With `core.autocrlf=true` on Windows, a
   checkout rewrote `dvc.lock`/`metrics.json` line endings, so the DVC-recorded md5 never matched
   and `dvc status` showed phantom changes. Esha made this *changes requested item 2* on
   [#11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11); Nimra fixed it in
   [#15](https://github.com/eshamaryam1/cooked-ml-collab/pull/15) with `* text=auto eol=lf` +
   `git add --renormalize .` (and the mandatory `git rm --cached -r . ; git reset --hard`
   refresh), and Esha re-verified `dvc status` clean end to end.
3. **Squash merges vs long-lived branches → rebase conflicts.** [#10](https://github.com/eshamaryam1/cooked-ml-collab/pull/10)
   had to be reopened, retargeted from its wrong base to `dev`, rebased, and stripped of a
   duplicated `#8` fix before Nimra could approve it; [#11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11)
   was rebased onto `2bf697b` after #14/#13 merged (its reviewer then re-verified on the new head);
   and #13/#14 were deliberately ordered so the `params.yaml` conflict happened in one
   reviewable place.
4. **`metrics.json` provenance drift.** Experiments must run on committed code — the SHA in
   `commit_sha` is whatever HEAD was at run time, so a run on a dirty tree logs the wrong
   provenance (the shipped file still carries the data-branch SHA `18b7027` because the pipeline
   was not re-run after later merges — content unchanged, only the provenance field is older).
   Standardised as a Module 07 gotcha and into CONTRIBUTING.
5. **Required checks gate the release PRs.** [#21](https://github.com/eshamaryam1/cooked-ml-collab/pull/21)
   and [#22](https://github.com/eshamaryam1/cooked-ml-collab/pull/22) sat `BLOCKED` with every job
   green purely on the 1-approval rule (an author cannot approve their own PR), and #20 proved the
   checks refuse a merge outright. The release train only moves as fast as the teammate is
   awake — plus a real handoff mid-project when Nimra's battery died and Esha took Module 08 over.
6. **Sync-back from `main` went `DIRTY` (today).** Because `staging`/`main` are **rebase**-merged,
   their history is a replayed copy of `dev`'s; cutting the sync PR branch from `main` gave a huge
   three-dot diff and real conflicts in the two hotfix files. Fixed by regenerating the branch as
   `dev` + `cherry-pick` of the hotfix ([#24](https://github.com/eshamaryam1/cooked-ml-collab/pull/24))
   — same content, zero conflict.

**What we standardised** (the lines that went into `CONTRIBUTING.md` as a result — see
"What actually bit us" in that file): raw CSV is DVC-only, never `git add`ed; `dvc push` before
`git push`; keep the tree LF and re-check `dvc status` after any cross-machine checkout; run
`dvc exp` only on committed code; rebase `feat/*` onto `dev` before review; **sync hotfixes back
into `dev` by cherry-picking onto a branch off `dev`, never by branching from `main`**; open the
release PRs early because required checks + 1 approval gate them.

## 9. Per-member contributions

| Member | Authored merged PRs | Reviewed (approved) for the other | Notable |
|---|---|---|---|
| **Esha** [@eshamaryam1](https://github.com/eshamaryam1) | #1, #5, #6, #8, #10, #14, #16, #17, #19 (+ #20, closed by design) | #2, #3, #4, #7, #9, #11 (changes requested → re-approved), #12, #13, #15, #18, #21, #22, #23, #24 | Model owner; repo owner; branch protection + required checks; Module 08 CI and its red-check checkpoint |
| **Nimra** [@Nimra-Saleem29](https://github.com/Nimra-Saleem29) | #2, #3, #4, #7, #9, #11, #12, #13, #15, #18, #21, #22, #23, #24 | #1, #5, #6, #8, #10, #14, #16, #17, #19 | Data + platform owner; pre-commit/secrets, DVC data, conflict pair, release train, hotfix, independent reproduction, this report |

Checklist cover (assignment step 8):

- [x] Repository link submitted — https://github.com/eshamaryam1/cooked-ml-collab
- [x] `REPORT.md` complete, no placeholders
- [x] `model-v1.0` tag on `main` (`e2449f8`) + [GitHub release](https://github.com/eshamaryam1/cooked-ml-collab/releases/tag/model-v1.0)
- [x] `model-v1.0.1` tag (hotfix done, `48c07f2`) + [release](https://github.com/eshamaryam1/cooked-ml-collab/releases/tag/model-v1.0.1)
- [x] Every member has 2+ authored and 2+ reviewed merged PRs (Esha 9 authored / 14 reviewed,
      Nimra 14 authored / 9 reviewed)
- [x] At least one "changes requested" review — Esha on [#11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11)
- [x] Three protected branches with required checks — `docs/evidence/09-branch-protection.txt`
- [x] No dataset, model file or secret anywhere in Git history — checkpoint 4 ☑,
      `docs/evidence/04-dvc-no-csv-history.png`, `.secrets.baseline`
- [x] `docs/PROGRESS.md` fully ticked — M01's single instructor-invite line stays open until the
      instructor's GitHub username is known
- [x] A stranger can reproduce: `git clone && git checkout model-v1.0 && uv sync && dvc pull && dvc repro`
      → proven by the fresh-clone run in §3
