# Module 04 — Version the data with DVC

**Owner:** Nimra (Data owner), reviewed by Esha
**Depends on:** Module 03 (the 1 MB large-file hook makes this module's approach mandatory)
**Branch:** `data/initial-dataset` → PR into `dev`
**Checkpoint:** the CSV is not in Git history; only its `.dvc` pointer is. Reviewer can `dvc pull`.

---

## Goal

The raw California Housing CSV tracked by DVC, stored in a shared remote, recoverable by the
teammate with one `dvc pull`.

## Before you start — verify the CSV hash matches

Both of you must have byte-identical `data/raw/california_housing.csv` (Module 02 step 5), because
DVC identifies data by content hash:

```bash
git hash-object data/raw/california_housing.csv
```

If these differ, stop and fix Module 02 step 5 before creating any `.dvc` pointer.

## Setup: create the DagsHub remote

1. Both members sign up at <https://dagshub.com> and verify their email.
2. Create a DagsHub repository for this project. Name it `cooked-ml-collab` (or
   `cooked-ml-collab-data` — one remote repo is enough).
3. On DagsHub, go to **Settings → Access Tokens** and create a token. Scope: `repo` (read/write on
   the data repo is enough; do not use a full account token in a shared repo if you can avoid it).

Credentials go in `.dvc/config.local`, which DVC gitignores automatically. Never commit a token.

## Steps

### 1. Branch and add DVC

```bash
git switch dev
git pull --ff-only
git switch -c data/initial-dataset

uv add "dvc[s3]"
```

### 2. Initialise DVC

```bash
uv run dvc init
```

`dvc init` creates `.dvc/`, `.dvcignore` and adds the following to `.gitignore`:

```
/.dvc/cache
```

`dvc init` works on a branch, so the `.dvc/` directory lands on `dev` through the PR — correct.

### 3. Track the raw CSV

```bash
uv run dvc add data/raw/california_housing.csv
```

This writes `data/raw/california_housing.csv.dvc` and appends the ignore entries to
`data/.gitignore`:

```gitignore
/raw/california_housing.csv
```

**The `.csv` is now untracked by Git but tracked by DVC.** Because the file exceeds the 1 MB
pre-commit limit, do **not** try to `git add` it — stage only the pointer:

```bash
git add .dvc/config .dvc/.gitignore .dvcignore data/raw/california_housing.csv.dvc data/.gitignore
git status
git commit -m "data: track raw california housing csv with dvc"
```

`.dvc/config` is safe to commit — it holds the **remote URL**, no credentials.

### 4. Configure the shared remote

```bash
uv run dvc remote add -d storage https://dagshub.com/<dagshub-user>/<dagshub-repo>.dvc
uv run dvc remote modify storage --local auth <your-dagshub-token>
```

The `--local` flag writes to `.dvc/config.local` (gitignored) — that is how the token never
reaches Git. Teammates do the same:

```bash
uv run dvc remote modify storage --local auth <your-dagshub-token>
```

Verify what is and is not tracked:

```bash
git check-ignore -v data/raw/california_housing.csv
git ls-files | Select-String -Pattern "\.csv$"
```

Expected: the CSV is ignored, and `git ls-files` shows only `.dvc` pointers and the small
`tests/fixtures/sample.csv` added in Module 08.

### 5. Push the data, then the code

```bash
uv run dvc push
git push -u origin data/initial-dataset
```

**`dvc push` first. Always.** If you `git push` without it, your teammate gets a `.dvc` pointer
whose object does not exist on the remote and `dvc pull` fails with a missing-object error.

### 6. Reviewer verification (Esha's job, and this is what makes it a real review)

Esha clones the branch into a **fresh folder**:

```bash
git clone --branch data/initial-dataset https://github.com/<esha>/cooked-ml-collab.git fresh-check
cd fresh-check
uv sync
uv run dvc remote modify storage --local auth <esha-dagshub-token>
uv run dvc pull
uv run dvc status
```

Expected: the CSV downloads, `dvc status` is clean, `dvc.lock`-free (no pipeline yet), and

```bash
uv run python -c "import pandas as pd; d=pd.read_csv('data/raw/california_housing.csv'); print(d.shape)"
```

prints `(20640, 9)`. Esha pastes the terminal output into the PR, then merges (squash) and
deletes the branch.

### 7. Prove the CSV never entered Git history

```bash
git log --all --oneline -- data/raw/california_housing.csv
git rev-list --objects --all | Select-String -Pattern "california_housing\.csv$"
```

Both should come back empty apart from the `.dvc` pointer. Screenshot this for `REPORT.md` — the
rubric explicitly checks "no data in Git history".

## Future data-version commands (used again in Module 07 step 4)

```bash
uv run dvc status          # what changed
uv run dvc push            # upload new version
uv run dvc checkout        # restore the version referenced by the current commit
uv run dvc checkout <old-sha>
uv run dvc push            # re-upload that old version
```

## Checkpoint evidence

- [x] `data/raw/california_housing.csv.dvc` is committed; the `.csv` is not in Git
- [x] `dvc push` completed and `dvc pull` on a fresh clone works
- [x] No token in `.dvc/config`; token only in the gitignored `.dvc/config.local`
- [x] `git log -- data/raw/california_housing.csv` shows nothing
- [x] PR reviewed with terminal output pasted, then merged and branch deleted

## Gotchas

- **Do not blanket-ignore a directory that will hold `.dvc` pointers.** dulwich (DVC's default
  git backend on this setup) treats a `dir/*` pattern as "the directory itself is ignored" and
  prunes it from the walk DVC uses to find `.dvc` files — `dvc status` then reports "no data
  tracked" and `dvc push` says "Everything is up to date" while uploading nothing. Let
  `dvc add` write `data/<dir>/.gitignore` per file instead (fixed in commit `5206509`).
- `detect-secrets` flags the pointer's md5 as a high-entropy secret — keep an inline
  `# pragma: allowlist secret` on the `md5:` line of the `.dvc` file (`dvc add` preserves it).
- DVC 3 remote auth is three settings, not one:
  `dvc remote modify storage --local auth basic` + `user` + `password` (token).

- If a dataset ever *does* land in history, `git rm` is not enough. Use
  `git filter-repo --path data/raw/california_housing.csv --invert-paths`, then force-push and tell
  your teammate to re-clone. Better to avoid it entirely.
- `dvc pull` on Windows: if a stale `.dvc/cache` confuses the download, `Remove-Item -Recurse -Force .dvc/cache` and pull again.
- DagsHub free repos have storage quotas; our CSV is ~2.4 MB so this is a non-issue, but large
  model artefacts in Module 06 should go to the same remote only if they stay small.
- Never run `dvc add -f` on the CSV and then `git add` it. The whole point is that Git never sees
  the bytes.
