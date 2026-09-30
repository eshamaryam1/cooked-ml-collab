# Playbook — team conventions

Agreed once as a team, binding for the whole project, and summarised in `CONTRIBUTING.md`
in Module 02. This file is the source of truth for us while we work.

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

## Conventional Commits

```
<type>(<optional scope>): <short imperative summary>
```

Types we use: `feat`, `fix`, `data`, `exp`, `chore`, `docs`, `refactor`, `test`, `ci`, `build`, `perf`.

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

Rationale: `dev` history stays readable and each merged PR is one commit that matches the PR
title; release branches keep a linear, non-rewritten history so a tag points at real individual
commits. Because `dev` gets squashed, short-lived branches must be rebased on `dev` before they
are reviewed so the PR diff is not noisy:

```
git fetch && git rebase origin/dev
git push --force-with-lease
```

`--force-with-lease` only, never plain `--force`.

## Merge strategy per target

| Target | Strategy |
|---|---|
| `dev` | Squash merge |
| `staging` | Rebase merge |
| `main` | Rebase merge |

## Pull request checklist

Copied verbatim into `.github/pull_request_template.md` in Module 02.

```markdown
## What changed and why

## Metrics (before → after)

## Review checklist
- [ ] No data leakage (no target or future information in features)
- [ ] Splits are fixed; preprocessing fit on training data only
- [ ] No hardcoded paths; runs on a teammate's machine
- [ ] Seeds set for shuffling, initialisation and sampling
- [ ] Metric computed the way the team reports it
- [ ] dvc push done before git push (if data or models changed)
- [ ] Notebook restarted and run top to bottom (if notebooks changed)
- [ ] Style and naming (linter passes)

## How the reviewer can verify
```

Reviewers: check out the branch at least once for any PR that touches `src/`, `dvc.yaml` or
`params.yaml`, and paste what you actually ran into the PR. Requesting changes at least once
during the project is a requirement, not a formality.

## Commands we use a lot

```
git switch -c feat/<name> dev
git fetch && git rebase origin/dev
git cherry-pick <sha>
dvc status
dvc push            # ALWAYS before git push
dvc pull            # fresh clone
dvc repro           # rebuild every stage
dvc repro --force   # rebuild even if DVC thinks nothing changed
dvc exp show
dvc checkout        # sync data files to the current commit
uv sync
uv run pytest tests/
uv run pre-commit run --all-files
```

## Where evidence goes

Everything the grader needs goes in `REPORT.md` at the repo root. Screenshots and metric tables
pasted from PRs go in `docs/evidence/` as you collect them, in Module 09.
