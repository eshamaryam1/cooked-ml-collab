"""Model construction and pipeline assembly."""

from __future__ import annotations

from typing import Any

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

from cooked_ml.features import make_preprocessor

MODEL_NAMES = ("random_forest", "linear_regression", "gradient_boosting")

# ``params.yaml`` carries one flat ``model.params`` block for every family, and
# experiments switch ``model.name`` without rewriting it. Keys the selected
# estimator does not accept are therefore dropped, while a key that belongs to
# no supported estimator is still an error instead of a silent typo.
MODEL_PARAMS: dict[str, frozenset[str]] = {
    "random_forest": frozenset({"n_estimators", "max_depth", "min_samples_leaf", "n_jobs"}),
    "gradient_boosting": frozenset({"n_estimators", "max_depth", "min_samples_leaf"}),
    "linear_regression": frozenset({"n_jobs"}),
}


def build_model(cfg: dict[str, Any], seed: int) -> Any:
    """Build the estimator named in ``params.yaml``.

    ``cfg`` is the ``model`` section; ``seed`` is applied to every estimator that
    can take one, so a rerun with the same parameters reproduces the same model.
    """
    name = cfg.get("name", "random_forest")
    if name not in MODEL_NAMES:
        raise ValueError(f"unknown model {name!r}, expected one of {MODEL_NAMES}")

    hyperparams = dict(cfg.get("params") or {})
    known = set().union(*MODEL_PARAMS.values())
    unknown = sorted(set(hyperparams) - known)
    if unknown:
        raise ValueError(f"unknown model param(s) {unknown} for {name!r}, expected {sorted(known)}")
    hyperparams = {key: value for key, value in hyperparams.items() if key in MODEL_PARAMS[name]}

    if name == "linear_regression":
        # closed-form least squares: nothing to seed, and no random_state kwarg
        return LinearRegression(**hyperparams)

    hyperparams["random_state"] = seed
    if name == "random_forest":
        return RandomForestRegressor(**hyperparams)
    return GradientBoostingRegressor(**hyperparams)


def build_pipeline(params: dict[str, Any], seed: int | None = None) -> Pipeline:
    """Preprocessing fitted on the training split plus the estimator."""
    seed = params["seed"] if seed is None else seed
    return Pipeline(
        steps=[
            ("preprocess", make_preprocessor(params)),
            ("model", build_model(params["model"], seed)),
        ]
    )
