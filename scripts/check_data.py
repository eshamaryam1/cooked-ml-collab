"""Schema, null and range checks for the raw CSV — runnable locally and in CI.

    uv run python scripts/check_data.py                                   # the committed sample
    uv run python scripts/check_data.py --data data/raw/california_housing.csv

No DVC and no network: CI runs this against ``tests/fixtures/ci_sample.csv``
(200 real rows) so the signal stays fast and credential-free. It is a sibling of
``tests/fixtures/sample.csv`` on purpose — that file is the *synthetic* M02
fixture the unit tests lean on (``test_pipeline_learns_the_synthetic_signal``),
not real housing data.

Range bounds were measured from the shipped dataset rather than taken from the
module doc's example table, which is wrong for four columns: the real extrema are
AveRooms 141.9, AveBedrms 34.07, Population 35682 and AveOccup 1243 — all above
the doc's illustrative caps. Bounds below are the measured min/max widened by a
small margin, so both the 200-row sample and the full 20,645-row CSV pass.
"""

from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

FEATURES = [
    "MedInc",
    "HouseAge",
    "AveRooms",
    "AveBedrms",
    "Population",
    "AveOccup",
    "Latitude",
    "Longitude",
]
TARGET = "MedHouseVal"
RANGES: dict[str, tuple[float, float]] = {
    "MedInc": (0.0, 15.01),
    "HouseAge": (0.0, 53.0),
    "AveRooms": (0.0, 150.0),
    "AveBedrms": (0.0, 35.0),
    "Population": (0.0, 40000.0),
    "AveOccup": (0.0, 1300.0),
    "Latitude": (32.5, 42.0),
    "Longitude": (-124.5, -114.3),
    "MedHouseVal": (0.0, 6.0),
}
MAX_NULLS = 0


def check(path: str) -> list[str]:
    errors: list[str] = []
    df = pd.read_csv(path)

    missing_cols = [c for c in [*FEATURES, TARGET] if c not in df.columns]
    if missing_cols:
        return [f"missing columns: {missing_cols}"]

    extra_cols = [c for c in df.columns if c not in [*FEATURES, TARGET]]
    if extra_cols:
        errors.append(f"unexpected columns: {extra_cols}")

    if len(df) == 0:
        errors.append("file has no rows")
        return errors

    for col in [*FEATURES, TARGET]:
        nulls = int(df[col].isna().sum())
        if nulls > MAX_NULLS:
            errors.append(f"{col}: {nulls} nulls (max {MAX_NULLS})")

    for col, (lo, hi) in RANGES.items():
        values = df[col].to_numpy(dtype=float)
        if not np.isfinite(values).all():
            errors.append(f"{col}: contains non-finite values")
            continue
        if values.min() < lo or values.max() > hi:
            errors.append(
                f"{col}: values outside [{lo}, {hi}] (got {values.min()}, {values.max()})"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="tests/fixtures/ci_sample.csv")
    args = parser.parse_args()

    try:
        errors = check(args.data)
    except FileNotFoundError:
        print(f"data-check: file not found: {args.data}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"data-check: {error}", file=sys.stderr)
        return 1

    print(f"data-check: ok ({args.data})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
