# Contributing to cooked-ml

Team **cooked** — Esha ([@eshamaryam1](https://github.com/eshamaryam1)) and
Nimra ([@Nimra-Saleem29](https://github.com/Nimra-Saleem29)).
Everyone codes and everyone reviews: every member needs **2 authored + 2 reviewed PRs**, and at
least one review must be *"Changes requested"*.

The full conventions live in [`docs/PLAYBOOK.md`](docs/PLAYBOOK.md); this file is the summary you
read before your first PR.

## Branching model

Work moves in one direction only: `dev` → `staging` → `main`, always through a reviewed PR with
passing CI.

| Branch | Created from | Merges into | Notes |
|---|---|---|---|
| `main` | — | — | Production + released models only. Every merge is tagged. |
| `staging` | `main` | `main` | Release candidate. Reproduced here before it ships. |
| `dev` | `staging` | `staging` | Integration branch. All finished work lands here. |
| `feat/<name>` | `dev` | `dev` | Production code. Small, short-lived, deleted after merge. |
| `data/<name>` | `dev` | `dev` | Dataset changes tracked with DVC. `dvc push` first. |
| `exp/<member>-<idea>` | `dev` | nothing | Exploration. Never merged directly. Cherry-pick winners. |
| `fix/<name>` | `main` | `main` → then back into `dev` | Urgent production fix, tagged `model-vX.Y.Z`. |

### Branch naming

Lowercase, hyphen-separated, prefixed with the type: `feat/split-determinism`,
`data/fix-null-rows`, `exp/nimra-leaf-tuning`, `chore/bump-ruff`.

### Create a branch

```bash
git switch -c feat/<name> dev
git fetch && git rebase origin/dev
```

Rebase on `dev` before you ask for review — `dev` is squash-merged, so an unrebased branch
produces a noisy PR diff. When you have to update a reviewed branch, use
`git push --force-with-lease`, never plain `--force`.

## Conventional Commits

```
<type>(<optional scope>): <short imperative summary>
```

Types we use: `feat`, `fix`, `data`, `exp`, `chore`, `docs`, `refactor`, `test`, `ci`, `build`,
`perf`.

```
feat: add scaling step
data: remove duplicate rows
exp: try max_depth=8
ci: add smoke train check
chore: pin environment with uv.lock
```

Rules: lowercase, no trailing period, one logical change per commit, `BREAKING CHANGE:` footer if
needed.

## Squash vs rebase — our decision

**We squash-merge into `dev` and rebase-merge into `staging` and `main`.**

| Target | Strategy |
|---|---|
| `dev` | Squash merge |
| `staging` | Rebase merge |
| `main` | Rebase merge |

Rationale: `dev` history stays readable and each merged PR is one commit that matches the PR
title; release branches keep a linear, non-rewritten history so a tag points at real individual
commits.

## Pull request checklist

This is copied verbatim into [`.github/pull_request_template.md`](.github/pull_request_template.md).

- What changed and why
- Metrics (before → after)
- No data leakage (no target or future information in features)
- Splits are fixed; preprocessing fit on training data only
- No hardcoded paths; runs on a teammate's machine
- Seeds set for shuffling, initialisation and sampling
- Metric computed the way the team reports it
- `dvc push` done before `git push` (if data or models changed)
- Notebook restarted and run top to bottom (if notebooks changed)
- Style and naming (linter passes)
- How the reviewer can verify

## Review rule

Reviewers must **actually run the code**, not just read the diff: check out the branch at least
once for any PR that touches `src/`, `dvc.yaml` or `params.yaml`, and paste what you really ran
into the PR. Requesting changes at least once during the project is a requirement, not a
formality.

## Commands we use a lot

```bash
git switch -c feat/<name> dev
git fetch && git rebase origin/dev
git cherry-pick <sha>
dvc status
dvc push            # ALWAYS before git push
dvc pull            # fresh clone
dvc repro           # rebuild every stage
dvc exp show
uv sync
uv run pytest tests/
uv run pre-commit run --all-files
```

## Setup

```bash
uv sync                      # creates .venv from uv.lock
uv run pre-commit install    # hooks run on every commit; do this once per clone
uv run python -m cooked_ml.cli train
uv run python -m cooked_ml.cli evaluate
uv run pytest tests/
```

`dvc push` before `git push`, every time — a missing `dvc push` leaves your teammate with a
broken pointer and they cannot reproduce anything.
