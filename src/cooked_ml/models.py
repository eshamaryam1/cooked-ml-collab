"""Model construction and pipeline assembly."""

from __future__ import annotations

from typing import Any

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

from cooked_ml.features import make_preprocessor

MODEL_NAMES = ("random_forest", "linear_regression", "gradient_boosting")


def build_model(cfg: dict[str, Any], seed: int) -> Any:
    """Build the estimator named in ``params.yaml``.

    ``cfg`` is the ``model`` section; ``seed`` is applied to every estimator that
    can take one, so a rerun with the same parameters reproduces the same model.
    """
    name = cfg.get("name", "random_forest")
    hyperparams = dict(cfg.get("params") or {})

    if name == "random_forest":
        hyperparams["random_state"] = seed
        return RandomForestRegressor(**hyperparams)
    if name == "linear_regression":
        return LinearRegression(**hyperparams)
    if name == "gradient_boosting":
        hyperparams["random_state"] = seed
        return GradientBoostingRegressor(**hyperparams)
    raise ValueError(f"unknown model {name!r}, expected one of {MODEL_NAMES}")


def build_pipeline(params: dict[str, Any], seed: int | None = None) -> Pipeline:
    """Preprocessing fitted on the training split plus the estimator."""
    seed = params["seed"] if seed is None else seed
    return Pipeline(
        steps=[
            ("preprocess", make_preprocessor(params)),
            ("model", build_model(params["model"], seed)),
        ]
    )
