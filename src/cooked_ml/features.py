"""Preprocessing.

The starter code fitted ``StandardScaler`` on the whole dataset before the split,
which leaks test information into training. Here the scaler lives inside a
pipeline that is only ever fitted on the training split, so ``fit`` and
``transform`` cannot be mixed up at the call site.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def build_preprocessor(
    *,
    scale: bool = True,
    impute_strategy: str = "median",
) -> Pipeline:
    """Return an unfitted preprocessing pipeline."""
    steps: list[tuple[str, Any]] = [("impute", SimpleImputer(strategy=impute_strategy))]
    if scale:
        steps.append(("scale", StandardScaler()))
    return Pipeline(steps=steps)


def make_preprocessor(params: dict[str, Any]) -> Pipeline:
    """Build the preprocessor described by ``params.yaml``."""
    settings = params.get("preprocessing", {})
    return build_preprocessor(
        scale=bool(settings.get("scale", True)),
        impute_strategy=str(settings.get("impute_strategy", "median")),
    )


def feature_columns(columns: Sequence[str], target: str) -> list[str]:
    """Drop the target from a column list, keeping the original order."""
    return [column for column in columns if column != target]
