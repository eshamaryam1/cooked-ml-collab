# Module 01 — Team & repository setup

**Owner:** both (Esha creates the repo, both configure their identity)
**Depends on:** nothing
**Branches:** none yet — the repo starts empty
**Checkpoint:** all members can push a branch

---

## Goal

A GitHub repo `cooked-ml-collab` with both members as write collaborators and the instructor as a
viewer. Everyone has a working local clone with their own `user.name` / `user.email`.

## Steps

### 1. Tell the instructor

Report the dataset choice (California Housing, from the starter repo
`mikel-brostrom/Housing_Price_Prediction`) **by the end of Phase 1**.

### 2. Create the remote repository — DONE

`cooked-ml-collab` already exists at <https://github.com/eshamaryam1/cooked-ml-collab>, created by
Esha. Verified state:

- Owner: `eshamaryam1`, empty (no commits), default branch `main`
- Visibility: **public** — chosen deliberately. The dataset is public, no credentials are ever
  committed, Actions minutes are unlimited on public repos, and the grader/instructor can always
  see the repository.

Collaborators still to add (Settings → Collaborators and teams, or with the GitHub CLI):

- Add `@Nimra-Saleem29` → **Write**
- Add the instructor → **Read** (viewer). **Not required** — team decision 2026-10-04: the repo is
  public, so the instructor/grader can read it without an invite and there is no username to add.

GitHub CLI is installed at `C:\Program Files\GitHub CLI\gh.exe` for this. After `gh auth login`:

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" repo collaborator add Nimra-Saleem29 -R eshamaryam1/cooked-ml-collab -p write
& "C:\Program Files\GitHub CLI\gh.exe" repo collaborator add <instructor-username> -R eshamaryam1/cooked-ml-collab -p read
& "C:\Program Files\GitHub CLI\gh.exe" repo view --web
```

> If the instructor must not be able to comment, use `read`; the assignment says "added as a viewer".

### 3. Clone and set identity

Esha — already done locally in `C:\Users\DELL\cooked-ml-collab`:

```bash
git config user.name  # eshamaryam1
git config user.email # eshamaryam11em@gmail.com
```

Nimra — on her machine:

```bash
git clone https://github.com/eshamaryam1/cooked-ml-collab.git
cd cooked-ml-collab
git config user.name "Nimra Saleem"
git config user.email "<nimra-github-email>"
```

Use the **same email address in both** the local `git config` and the GitHub account email
settings, otherwise GitHub will not link your commits to your profile and the grader cannot see
who authored what. Check with **Settings → Emails** on GitHub.

> The email must be verified on GitHub or contributions do not show up on the profile.


### 4. Assign roles (done)

- **Esha — Model owner**: training pipeline, `params.yaml`, `dvc.yaml`, experiments, notebooks
- **Nimra — Data owner + Platform owner**: DVC + remote, data checks, data-update PR, pre-commit,
  CI, releases

The Platform owner role is split between two people in a team of 2, as the assignment requires.

### 5. Prove both members can push

Esha — done, 2026-09-29. Branch `chore/check-push-esha`, root commit `87d044c`, confirmed present
on the remote and attributed to `eshamaryam1` by GitHub.

Nimra, in her own clone:

```bash
git clone https://github.com/eshamaryam1/cooked-ml-collab.git
cd cooked-ml-collab
git config user.name "Nimra Saleem"
git config user.email "<nimra-github-email>"
git switch -c chore/check-push-nimra origin/chore/check-push-esha
git commit --allow-empty -m "chore: verify nimra can push"
git push -u origin chore/check-push-nimra
```

Either delete these throwaway branches afterwards, or keep them — they are harmless evidence that
both accounts have write access. Do **not** merge them into `main`.

> This creates two unrelated root commits in the remote (the throwaway branch and, later, the
> Module 02 import on `main`). That is harmless — git keeps them separate and nothing in `main`
> depends on the throwaway branch.

### 6. Enable Actions for the repo

Settings → Actions → General → **Allow GitHub Actions to create and approve pull requests**
(enabled). Also confirm Actions minutes / status is not disabled for the account, because Module
08 depends on it.

## Checkpoint evidence

- [x] Repo exists with both members at Write (instructor-viewer invite **not required** — team
  decision 2026-10-04, the repo is public)
- [x] Each member has at least one pushed commit under their own name
- [x] `git log` in each clone shows the author name and email matching GitHub

Verify attribution:

```bash
git log --all --format="%an <%ae> | %s"
```

## Gotchas

- A collaborator invited by email may sit at **Pending** until they accept. Check
  Settings → Collaborators before assuming you can push.
- Do not initialise the repo with a README on GitHub and also locally — the histories diverge and
  Module 02's `staging`/`dev` creation gets confusing.
