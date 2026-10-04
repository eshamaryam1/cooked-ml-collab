# Module 09 evidence — independent reproduction of `model-v1.0`

Captured 2026-10-04 by @Nimra-Saleem29 (the member who did **not** train the final model —
Esha promoted the gradient booster in Module 07). Companion of the comment on
[PR #21](https://github.com/eshamaryam1/cooked-ml-collab/pull/21#issuecomment-5983279345).

The run happens in a brand-new clone outside the working repo, on the release head
`cf57ca7` — the exact tree [PR #21](https://github.com/eshamaryam1/cooked-ml-collab/pull/21)
shipped onto `staging` (the PR was not merged yet at reproduction time, so the PR head *is*
the released content; `staging` after the rebase merge and `main` carry the same tree —
`git diff origin/staging origin/dev` → empty, `metrics.json` blob `e828f98` on both sides).

## Commands

```text
$ git clone https://github.com/eshamaryam1/cooked-ml-collab.git release-check
$ cd release-check
$ git checkout cf57ca7
HEAD is now at cf57ca7 ci: run lint, tests, data-check and smoke train on every pull request (#19)

$ uv sync                                    # deps from uv.lock, fresh .venv
$ uv run dvc remote modify storage --local auth basic
$ uv run dvc remote modify storage --local user Nimra-Saleem29
$ uv run dvc remote modify storage --local password ******
$ uv run dvc pull
4 files fetched and 4 files added            # raw csv 1,426,634 bytes = dvc.lock size
                                              # data/processed/{train,test}.csv, models/model.joblib

$ uv run dvc repro --force                   # real end-to-end rerun, not a cache hit
$ uv run dvc status
Data and pipelines are up to date.

$ git rev-parse HEAD
cf57ca7ecba593f2a0a46b0fdbf7e4609ad4083b
$ git tag --points-at HEAD
(empty — `model-v1.0` is tagged on the merged `main` tip in step 4)
```

## metrics.json — released vs fresh run

Released (committed on the release head):

```json
{
  "r2": 0.8415635827935704,
  "mae": 0.294844375210418,
  "n_train": 16512,
  "n_test": 4128,
  "seed": 42,
  "commit_sha": "18b7027dc3b63ea576f30084f0e2a0320cc1c4ff",
  "params": {
    "model": "gradient_boosting",
    "n_estimators": 200,
    "max_depth": 8,
    "min_samples_leaf": 1,
    "test_size": 0.2,
    "scale": true,
    "drop_duplicates": true,
    "max_rows": null
  },
  "data": {
    "raw_path": "data/raw/california_housing.csv",
    "raw_sha256": "130b4a03a5ae54a47acca4a6797203b4da62afadf6349259fab6fb4085c6dc5d",
    "raw_dvc_md5": "8a862f33970de79c84a533bf841050cc"
  }
}
```

Fresh `dvc repro --force` in the new clone:

```json
{
  "r2": 0.8415635827935704,
  "mae": 0.294844375210418,
  "n_train": 16512,
  "n_test": 4128,
  "seed": 42,
  "commit_sha": "cf57ca7ecba593f2a0a46b0fdbf7e4609ad4083b",
  "params": {
    "model": "gradient_boosting",
    "n_estimators": 200,
    "max_depth": 8,
    "min_samples_leaf": 1,
    "test_size": 0.2,
    "scale": true,
    "drop_duplicates": true,
    "max_rows": null
  },
  "data": {
    "raw_path": "data/raw/california_housing.csv",
    "raw_sha256": "130b4a03a5ae54a47acca4a6797203b4da62afadf6349259fab6fb4085c6dc5d",
    "raw_dvc_md5": "8a862f33970de79c84a533bf841050cc"
  }
}
```

| Field | Released | Fresh run | Match |
|---|---|---|---|
| r2 | 0.8415635827935704 | 0.8415635827935704 | exact |
| MAE | 0.294844375210418 | 0.294844375210418 | exact |
| n_train / n_test | 16512 / 4128 | 16512 / 4128 | exact |
| seed | 42 | 42 | exact |
| params block | identical | identical | exact |
| raw_sha256 | 130b4a03…dc5d | 130b4a03…dc5d | exact |
| raw_dvc_md5 | 8a862f33…50cc | 8a862f33…50cc | exact |
| commit_sha | 18b7027… | cf57ca7… | differs **by design** |

`commit_sha` is the only difference and it is not a metric: `config.current_commit_sha()`
records `git rev-parse HEAD` of whichever checkout produced the run, so any rerun in any clone
legitimately records that clone's HEAD.

## Whole-tree diff after the forced rerun

```text
$ git status --short
 M data/raw/california_housing.csv.dvc
 M dvc.lock
 M metrics.json

$ git diff -- metrics.json        # exactly one line: commit_sha (above)
$ git diff -- dvc.lock            # exactly one line:
                                  #   outs[metrics.json].md5 4360f64b875ac1c087b0c02cb836b052
                                  #                           → a76d3212372b1f2066becffb1d1bbaa8
                                  #   (consequence of commit_sha; size 595 unchanged)
$ git diff -- data/raw/california_housing.csv.dvc   # no content change (LF notice only)
```

Every **other** dependency and output md5 in `dvc.lock` is unchanged — the processed
`train.csv` (`26a4ba5d…`), `test.csv` (`c9371e93…`) and `models/model.joblib` (`6b47afe7…`)
reproduced **byte-for-byte**.

**Verdict: the released artefact reproduces exactly.** `dvc status` on the fresh clone reports
*up to date* afterwards, and `model-v1.0` (tagged on `main` at `e2449f8` after the rebase merge
of [PR #22](https://github.com/eshamaryam1/cooked-ml-collab/pull/22)) points at that content.
