# Module 07 — Experiments and pull requests

**Owner:** both (this is where the collaboration actually happens)
**Depends on:** Module 06
**Branches:** `exp/esha-*`, `exp/nimra-*` (never merged), plus `feat/*` and `data/*` for promotions
**Checkpoint:** every member appears as both author and reviewer, with at least one
"changes requested" review

---

## Goal

Six experiments (3 each), a promoted winner, a data update, a real resolved conflict, and an
abandoned experiment branch.

## Step 1 — Experiments (3 per member)

Each member branches from `dev` and never merges it:

```bash
git switch dev
git pull --ff-only
git switch -c exp/esha-max-depth
uv run dvc pull
```

**Never run experiments on uncommitted code** — the SHA logged in `metrics.json` must match the
code. Check first:

```bash
git status --porcelain
```

If it prints anything, commit or stash before experimenting.

Esha's three:

```bash
uv run dvc exp run --name exp-esha-d10 --set-param train.max_depth=10
uv run dvc exp run --name exp-esha-d4  --set-param train.max_depth=4
uv run dvc exp run --name exp-esha-gbr --set-param train.model=gradient_boosting
```

Nimra's three:

```bash
uv run dvc exp run --name exp-nimra-d8   --set-param train.max_depth=8
uv run dvc exp run --name exp-nimra-n300 --set-param train.n_estimators=300
uv run dvc exp run --name exp-nimra-ldm  --set-param train.model=linear_regression
```

Compare:

```bash
uv run dvc exp show
uv run dvc exp show --md
```

The Markdown table is what goes into the PR description and `REPORT.md`:

```
| Experiment        | Head SHA | Params                     | r2       | MAE      |
|-------------------|----------|----------------------------|----------|----------|
| base              | 3f9a1c2  | max_depth=6                | 0.8157   | 0.2812   |
| exp-esha-d10      | a1b2c3d  | max_depth=10               | 0.8241   | 0.2769   |
| exp-esha-d4       | b2c3d4e  | max_depth=4                | 0.7985   | 0.3104   |
| exp-esha-gbr      | c3d4e5f  | model=gradient_boosting    | 0.8310   | 0.2698   |
| exp-nimra-d8      | d4e5f60  | max_depth=8                | 0.8203   | 0.2790   |
| exp-nimra-n300    | e5f6071  | n_estimators=300           | 0.8272   | 0.2741   |
| exp-nimra-ldm     | f607182  | model=linear_regression    | 0.5760   | 0.4673   |
```

(Replace with real numbers. Note the linear regression row: it is a useful negative result and shows
the comparison is honest.)

Keep the `exp/` branches alive as evidence:

```bash
git push -u origin exp/esha-max-depth
git push -u origin exp/nimra-n300
```

## Step 2 — Promote the winner

```bash
git switch dev
git switch -c feat/promote-best-model
uv run dvc exp apply exp-esha-gbr
git diff
uv run dvc repro
Get-Content metrics.json
uv run dvc push
git add params.yaml dvc.lock metrics.json
git commit -m "feat: promote gradient boosting with r2 0.8310 from exp-esha-gbr"
git push -u origin feat/promote-best-model
```

`dvc exp apply` writes the winning params into `params.yaml` and restores `dvc.lock`. Commit the
result — the PR body must show **before → after**:

```
Before: r2 0.8157  MAE 0.2812  (random_forest, max_depth=6)
After:  r2 0.8310  MAE 0.2698  (gradient_boosting)
```

Add the `dvc exp show` table to the PR description too.

## Step 3 — Review each other

Every PR gets the teammate as reviewer. Rules:

- **≥2 authored and ≥2 reviewed merged PRs per member.**
- **At least one review with "Changes requested"** somewhere in the project. Do not engineer a fake
  one — wait for something genuinely worth pushing back on, then push back properly and say why.
- Reviewers of pipeline PRs must check out the branch and run it. Paste the actual terminal output
  into the PR, not just an approval.

## Step 4 — Data update

Nimra (Data owner) opens `data/drop-duplicates`:

```bash
git switch dev
git pull --ff-only
git switch -c data/drop-duplicates
uv run dvc pull
uv run dvc status
```

Make a real, documented change. Recommended: set `data.drop_duplicates: true` and add a genuine
row-count difference to the processed output, or append a handful of corrected rows. Then show the
version switch, which is what the rubric wants:

```bash
uv run dvc repro
uv run dvc push
git add data/raw/california_housing.csv.dvc dvc.lock params.yaml
git commit -m "data: enable duplicate removal in preprocessing"

git log --oneline -2 -- data/raw/california_housing.csv.dvc

# v1 — the old pointer. origin/dev still points at it: on PR #11's branch that commit is
# HEAD~2, not HEAD~1, because the data change took two commits (.dvc bump, then lock re-record)
git checkout origin/dev -- data/raw/california_housing.csv.dvc
uv run dvc checkout
Get-FileHash data/raw/california_housing.csv -Algorithm MD5   # old md5

# v2 — the new pointer this branch introduces
git checkout HEAD -- data/raw/california_housing.csv.dvc
uv run dvc checkout
Get-FileHash data/raw/california_housing.csv -Algorithm MD5   # new md5
```

Two different MD5s = the old data version is recoverable. Screenshot both hashes for `REPORT.md`.

## Step 5 — Resolve a real conflict

This one has to be coordinated. Do not fake it — the point is that two people edited the same
line.

1. Both branches are cut from `dev` **before** either is merged:

```bash
# Esha
git switch dev && git switch -c feat/tune-depth-esha

# Nimra, in her own clone
git switch dev && git switch -c feat/tune-estimators-nimra
```

2. Each edits a **different line of `params.yaml`** — but the same block, so the hunks overlap.
   Esha changes `train.max_depth: 6 → 8`. Nimra changes `train.n_estimators: 100 → 200`, and moves
   the `train:` block by one line so the diff context collides.

   ```bash
   git commit -am "feat: raise forest max depth to 8"
   git push -u origin feat/tune-depth-esha
   ```

   ```bash
   git commit -am "feat: raise forest estimators to 200"
   git push -u origin feat/tune-estimators-nimra
   ```

3. Esha's PR merges first.

4. Nimra rebases and resolves:

   ```bash
   git fetch origin
   git rebase origin/dev
   ```

   Git will stop on a conflict in `params.yaml`. Resolve it **intentionally** — both changes are
   wanted here:

   ```yaml
   train:
     model: random_forest
     n_estimators: 200
     max_depth: 8
     min_samples_leaf: 1
   ```

   ```bash
   git add params.yaml
   git rebase --continue
   uv run dvc repro
   uv run dvc push
   git add dvc.lock metrics.json
   git commit --amend -m "feat: raise forest estimators to 200 (max_depth 8 kept from esha)"
   git push --force-with-lease
   ```

5. Nimra documents in the PR body: which commit conflicted, what the two intents were, why the
   merge keeps both, and the metrics before and after. Esha confirms that is what she intended.

> If the rebase is genuinely trivial, add a whitespace-level difference so the conflict is real but
> still resolvable in minutes. Do not manufacture a conflict so nasty that it eats an evening.

## Step 6 — Experiment drift

Keep at least one `exp/` branch that is **never merged**, and explain in `REPORT.md` why it was
abandoned. The `exp-nimra-ldm` linear-regression experiment is a natural candidate — record its
metrics and state plainly that it underperformed (r2 ≈ 0.58) and that promoting it would have hurt
the released model.

```bash
git push -u origin exp/nimra-ldm
git branch -r | Select-String "exp/"
```

The branch stays on the remote as evidence.

## Update the trackers

Fill in the PR log, experiment table and abandoned-branch box in
[`PROGRESS.md`](PROGRESS.md) as you go.

## Checkpoint evidence

- [x] 3 experiments per member, compared with `dvc exp show`, table pasted into a PR
- [x] Winner applied with `dvc exp apply` and promoted via `feat/` PR with before/after metrics
- [x] `≥2` merged PRs authored per member and `≥2` reviewed per member
- [x] At least one "Changes requested" review — Esha on [PR #11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11)
  (2026-10-04); both items were fixed by Nimra in
  [PR #15](https://github.com/eshamaryam1/cooked-ml-collab/pull/15) and verified by Esha on #11 —
  still needs linking in `REPORT.md` (Module 09)
- [x] Data-update PR showing old and new data versions via `dvc checkout` —
  [PR #11](https://github.com/eshamaryam1/cooked-ml-collab/pull/11) (open; v1 `b2a3a690…` vs v2
  `8a862f33…` both reproduced in the body; branch now conflicts with `dev` after #14 and #13 —
  one `params.yaml` / `dvc.lock` / `metrics.json` rebase left before merge)
- [x] Conflict-resolution PR documented — [PR #13](https://github.com/eshamaryam1/cooked-ml-collab/pull/13):
  rebased onto [PR #14](https://github.com/eshamaryam1/cooked-ml-collab/pull/14)'s `4906d30`,
  `params.yaml` conflict output pasted in the body, both intents kept (`max_depth: 8` +
  `n_estimators: 200`), r2 0.84156. Esha approved after checking the branch out and running it —
  squash-merged as `2bf697b`, 2026-10-04
- [x] One unmerged `exp/` branch with a written explanation
- [x] Every PR used the checklist template

## Gotchas

- `dvc exp run` refuses to run with uncommitted changes in some versions; commit first.
- Experiment branches with a `.dvc` remote still share one workspace cache — do not run two
  `dvc exp run` processes concurrently in the same clone.
- `dvc exp apply` only touches tracked params/lock files; untracked edits in `src/` are **not**
  applied. Put code changes in a `feat/` branch via `git cherry-pick`, params via `dvc exp apply`.
- `git push --force-with-lease`, never `--force`, after a rebase.
