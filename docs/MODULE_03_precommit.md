# Module 03 — Guard rails: pre-commit and secrets

**Owner:** Nimra (Platform owner), reviewed by Esha
**Depends on:** Module 02
**Branch:** `feat/pre-commit` → PR into `dev`
**Checkpoint:** committing a 5 MB file and a fake API key are both blocked. Screenshot both.

---

## Goal

A pre-commit configuration that mechanically stops large files and secrets before they reach Git
history, plus local formatting so CI stays green.

## Steps

### 1. Branch and install

```bash
git switch dev
git pull --ff-only
git switch -c feat/pre-commit
uv add --dev pre-commit detect-secrets
uv run pre-commit install
```

Both members run `uv run pre-commit install` in their own clone. Add `pre-commit` to
`CONTRIBUTING.md` setup instructions so nobody forgets.

### 2. `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-added-large-files
        args: ["--maxkb=1024"]
      - id: check-merge-conflict
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: mixed-line-ending
        args: ["--fix=lf"]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format

  - repo: https://github.com/kynan/nbstripout
    rev: v1.9.1
    hooks:
      - id: nbstripout
        args: ["--extra-keys=E402,E999"]
        exclude: "^notebooks/.*\.py$"

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.24.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
```

Notes:

- `nbstripout` also strips execution counts, which Module 05's checkpoint checks for.
- The `.py` twin produced by `jupytext` in Module 05 must be excluded from `nbstripout` or the
  hook will try to parse a percent-format script as a notebook.
- Use **either** gitleaks **or** detect-secrets as the secret scanner; the assignment says "such as
  detect-secrets or gitleaks". Running both is fine and looks thorough, but commit
  `.secrets.baseline` if you use detect-secrets.

### 3. Baseline the secret scanner

```bash
uv run detect-secrets scan > .secrets.baseline
```

Review it and commit. Never commit the baseline of your *own* real credentials.

### 4. Ruff config in `pyproject.toml`

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "NPY"]
ignore = ["E501"]
```

Module 08's CI runs exactly `ruff check` and `ruff format --check`, so the local hook and CI must
agree.

### 5. Run it on everything

```bash
uv run pre-commit run --all-files
uv run ruff format .
git add -A
git commit -m "chore: add pre-commit hooks for lint, notebooks, large files and secrets"
```

### 6. Demonstrate both blocks (this is the graded evidence)

**Large file:**

```bash
uv run python -c "open('big_blob.bin','wb').write(b'0' * 5 * 1024 * 1024)"
git add big_blob.bin
```

Expected:

```
check-added-large-files ....... Failed
- hook id: check-added-large-files
- exit code: 1
- files were modified by this hook

Fix large files introduced by this commit:
big_blob.bin (5.0 MB exceeds 1024 KB limit)
```

```bash
git reset big_blob.bin
Remove-Item big_blob.bin
```

**Fake secret** (never commit this file):

```bash
@'
api_key = "sk-live-0123456789abcdefghijklmnopqrstuvwxyz"
aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
'@ | Set-Content -Encoding ascii demo_secret.py
git add demo_secret.py
```

Expected: `gitleaks ... Failed` and/or `detect-secrets ... Failed`.

```bash
git reset demo_secret.py
Remove-Item demo_secret.py
```

**Screenshot both failures.** They go in `docs/evidence/03-precommit-large-file.png` and
`docs/evidence/03-precommit-secret.png`, referenced from `REPORT.md`.

Also screenshot the successful run:

```bash
uv run pre-commit run --all-files
```

### 7. PR

```bash
git push -u origin feat/pre-commit
```

Open PR `feat/pre-commit → dev`. Esha reviews, checks out the branch, runs
`uv run pre-commit run --all-files` locally, pastes the output, and merges (squash).

## Checkpoint evidence

- [x] A 5 MB file is refused with `check-added-large-files`
- [x] A fake API key is refused by the secret scanner
- [x] Both screenshots saved under `docs/evidence/`
- [x] `uv run pre-commit run --all-files` passes clean
- [x] PR reviewed and merged into `dev`; branch deleted

## Gotchas

- `--maxkb=1024` is exactly 1 MB. The raw CSV (~2.4 MB) must therefore never be `git add`ed —
  in Module 04 you only stage the `.dvc` pointer and `data/.gitignore`.
- First run downloads hook environments; it takes a minute and needs network access.
- If a hook rewrites files and blocks the commit, stage the rewritten files and commit again.
- `--force-with-lease` only when rebasing pushed branches (see PLAYBOOK).
