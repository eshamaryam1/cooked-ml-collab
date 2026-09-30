# Module 09 — Release: dev → staging → main, tag, report

**Owner:** both
**Depends on:** Modules 01-08
**Branches:** `dev → staging`, `staging → main`, then tag `model-v1.0`
**Checkpoint:** `model-v1.0` exists on `main` and the independent reproduction succeeded

---

## Goal

A release PR into `staging`, an independent reproduction that matches exactly, a PR into `main`,
the `model-v1.0` tag, and a complete `REPORT.md`.

## Step 1 — Release PR dev → staging

```bash
git switch dev
git pull --ff-only
git log --oneline origin/dev ^origin/staging
```

That diff is what you are shipping. Summarise it, then open the PR on GitHub:

- base: `staging`, compare: `dev`
- title: **`release: v1.0`**
- body: list the included PRs (links), the final metrics table, the params that produced them, the
  data `.dvc` hash, and the seed.

```markdown
## Included PRs
- #12 feat: add seeded dvc pipeline producing reproducible metrics
- #14 feat: promote gradient boosting with r2 0.8310
- #17 data: enable duplicate removal in preprocessing

## Released model
| Field | Value |
|---|---|
| seed | 42 |
| model | gradient_boosting |
| test_size | 0.2 |
| raw data .dvc md5 | d3f07384d113edec49eaa6238ad5ff00 |
| r2 | 0.8310 |
| MAE | 0.2698 |

## Reproduces with
git clone <repo> && git checkout staging && uv sync && dvc pull && dvc repro
```

Reviewer: the teammate. **Approve only after running the commands below** (step 2).

Merge with **rebase merge** (per our PLAYBOOK decision) after CI is green.

## Step 2 — Independent reproduction (the graded checkpoint)

The member who did **not** train the final model does this in a brand-new folder. Say Esha trained
it, so **Nimra** reproduces.

```bash
cd C:\Users\DELL
git clone https://github.com/<esha-username>/cooked-ml-collab.git release-check
cd release-check
git checkout staging
uv sync
uv run dvc remote modify storage --local auth <nimra-dagshub-token>
uv run dvc pull
uv run dvc repro
Get-Content metrics.json
```

Compare with Esha's `metrics.json` from the release PR. They must match **exactly** — same R², same
MAE, same counts. Paste both files into the release PR thread as a comment.

Then prove the released artefact is the one:

```bash
uv run dvc status
git rev-parse HEAD
git tag --points-at HEAD
```

If `dvc repro` says "every stage is up to date" that is also a valid pass — it means the committed
`dvc.lock` and outputs are already consistent. Force a real rerun to be sure:

```bash
uv run dvc repro --force
Get-Content metrics.json
```

Save this as the reproducibility evidence: `docs/evidence/09-reproduction.md`, containing both
`metrics.json` files side by side.

## Step 3 — Release PR staging → main

Open the PR on GitHub:

- base: `main`, compare: `staging`
- title: `release: model-v1.0`
- body: same summary, plus a link to the reproduction comment from step 2

Get approval, wait for CI, **rebase merge**.

## Step 4 — Tag the release

```bash
git switch main
git pull --ff-only origin main
git log -1 --oneline
git tag -a model-v1.0 -m "First production model"
git push origin model-v1.0
```

Verify:

```bash
git tag -n
git show model-v1.0 --stat
```

Also create the GitHub release so the tag is visible on the repo page:

```bash
gh release create model-v1.0 --title "model-v1.0" --notes "California housing regression, R2 0.8310, MAE 0.2698"
```

## Step 5 — Optional hotfix (+5 with the release)

Find a small real bug on `main`. Good candidates: a metric rounded incorrectly, a missing null
guard, a misleading log message. Something you can demonstrate is wrong on `main`.

```bash
git switch main
git pull --ff-only
git switch -c fix/guard-empty-model
```

```bash
# edit src/cooked_ml/evaluate.py
git commit -am "fix: raise a clear error when metrics.json cannot be written"
git push -u origin fix/guard-empty-model
```

PR `fix/guard-empty-model → main`, approval, CI green, rebase merge. Then:

```bash
git switch main
git pull --ff-only
git tag -a model-v1.0.1 -m "Fix: guard empty metrics write"
git push origin model-v1.0.1
```

Then push the fix back down so it is not lost in the next release — as a PR, because `dev` is
protected:

```bash
git switch dev
git merge --no-ff main -m "merge main back into dev after model-v1.0.1"
git push origin dev
```

Since `dev` is protected, open a PR instead:

```bash
git switch main
git switch -c fix/sync-main-to-dev
git merge --no-ff main
git push -u origin fix/sync-main-to-dev
```

PR `fix/sync-main-to-dev → dev`. This satisfies "then back into dev".

## Step 6 — Retrospective

Meet for 20 minutes. Answer, concretely:

- What broke? (likely candidates: the 1 MB large-file hook vs the 2.4 MB CSV; `git push` before
  `dvc push`; the data-leakage bug inherited from the starter code; rebase conflicts after squash
  merges; CI required checks blocking the release PR)
- What would you standardise?
- What concrete lines did you add to `CONTRIBUTING.md` as a result?

Write it up in the "Retrospective" section of `REPORT.md`. It must name real incidents, not
generalities — the grader reads for specifics.

## Step 7 — REPORT.md

Final structure, at the repo root. Everything must be visible in the repository.

```markdown
# REPORT — cooked-ml-collab

## 1. Team
| Member | GitHub | Roles | Contribution |
|---|---|---|---|
| Esha  | @<username> | Model owner | one paragraph |
| Nimra | @<username> | Data + Platform owner | one paragraph |

## 2. Dataset and starter code
- Dataset: California Housing (regression), 20,640 rows x 8 features, target MedHouseVal
- Source: https://github.com/mikel-brostrom/Housing_Price_Prediction
- Underlying data: sklearn.datasets.fetch_california_housing
- What we changed from the starter code (scalers, seeding, torch dropped, CLI added)

## 3. Reproducibility table for model-v1.0
| Field | Value |
|---|---|
| Tag | model-v1.0 |
| Commit SHA | |
| params.yaml values | |
| Raw data .dvc hash | |
| dvc.lock md5 | |
| Seed | |
| Final metrics | r2 = , MAE = |
| Independent reproduction (by Nimra) | r2 = , MAE = — matches |

## 4. Experiments
- dvc exp show table for all 6 experiments
- why the winner was chosen

## 5. Required links
- Data update PR:
- Conflict resolution PR:
- A "changes requested" review:
- Release PR dev -> staging:
- Release PR staging -> main:
- Abandoned exp/ branch:

## 6. Screenshots
| What | File |
|---|---|
| Large file blocked | docs/evidence/03-precommit-large-file.png |
| Secret blocked | docs/evidence/03-precommit-secret.png |
| Failing CI | docs/evidence/08-ci-failing.png |
| Passing CI | docs/evidence/08-ci-passing.png |

## 7. Branching and protection
- screenshot of the three branch rules

## 8. Retrospective

## 9. Per-member contributions
```

Add all the numbers from the real runs — do not leave placeholders.

## Step 8 — Final submission checklist

- [ ] Repository link submitted
- [ ] `REPORT.md` complete, no placeholders
- [ ] `model-v1.0` tag on `main`
- [ ] `model-v1.0.1` tag if the hotfix was done
- [ ] Every member has 2+ authored and 2+ reviewed merged PRs
- [ ] At least one "changes requested" review
- [ ] Three protected branches with required checks
- [ ] No dataset, model file or secret anywhere in Git history
- [ ] `docs/PROGRESS.md` fully ticked
- [ ] A stranger can reproduce: `git clone && git checkout model-v1.0 && uv sync && dvc pull && dvc repro`

## Gotchas

- `dvc pull` on a tag: cloning with `--branch model-v1.0` gives you a detached HEAD. That is fine,
  `dvc repro` still works.
- The release PR into `main` is protected and has required checks. Start it early; do not rush the
  tag.
- Tag only the commit that is on `main` after the merge. Tagging locally before pushing the merge
  points at the wrong SHA.
- If CI is red on `staging` because `main` never had the new checks, that is expected — run the
  workflow once on `staging` and require the checks there before making them required on `main`.
