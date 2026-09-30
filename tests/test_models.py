"""Tests for model construction and for the no-leakage fitting contract."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression

from cooked_ml.cli import compute_metrics, parse_args
from cooked_ml.config import load_params
from cooked_ml.data import build_splits, load_raw
from cooked_ml.features import feature_columns, make_preprocessor
from cooked_ml.models import build_model, build_pipeline

FIXTURE = Path(__file__).parent / "fixtures" / "sample.csv"
SEED = 42


@pytest.fixture
def frame() -> pd.DataFrame:
    return load_raw(FIXTURE)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("random_forest", RandomForestRegressor),
        ("linear_regression", LinearRegression),
        ("gradient_boosting", GradientBoostingRegressor),
    ],
)
def test_build_model_returns_requested_family(name: str, expected: type) -> None:
    model = build_model({"name": name, "params": {}}, seed=SEED)
    assert isinstance(model, expected)


def test_build_model_rejects_unknown_family() -> None:
    with pytest.raises(ValueError, match="unknown model"):
        build_model({"name": "transformer", "params": {}}, seed=SEED)


def test_build_model_applies_seed() -> None:
    forest = build_model({"name": "random_forest", "params": {}}, seed=7)
    boosted = build_model({"name": "gradient_boosting", "params": {}}, seed=7)
    assert forest.random_state == 7
    assert boosted.random_state == 7


def test_build_model_passes_hyperparameters() -> None:
    forest = build_model({"name": "random_forest", "params": {"n_estimators": 7}}, seed=SEED)
    assert forest.n_estimators == 7


def test_build_model_is_reproducible(frame: pd.DataFrame) -> None:
    features = feature_columns(frame.columns, "MedHouseVal")
    first = build_model({"name": "random_forest", "params": {"n_estimators": 5}}, seed=SEED)
    second = build_model({"name": "random_forest", "params": {"n_estimators": 5}}, seed=SEED)
    first.fit(frame[features], frame["MedHouseVal"])
    second.fit(frame[features], frame["MedHouseVal"])
    assert np.allclose(first.predict(frame[features]), second.predict(frame[features]))


def test_scaler_is_fitted_on_training_split_only(frame: pd.DataFrame) -> None:
    train_frame, _ = build_splits(frame, test_size=0.2, seed=SEED)
    features = feature_columns(frame.columns, "MedHouseVal")

    pipeline = build_pipeline(load_params())
    pipeline.fit(train_frame[features], train_frame["MedHouseVal"])
    scaler = pipeline.named_steps["preprocess"].named_steps["scale"]

    assert np.allclose(scaler.mean_, train_frame[features].mean().to_numpy())
    assert not np.allclose(scaler.mean_, frame[features].mean().to_numpy())


def test_preprocessor_has_not_been_fitted_before_training() -> None:
    preprocessor = make_preprocessor(load_params())
    assert not hasattr(preprocessor.named_steps["impute"], "statistics_")


def test_pipeline_learns_the_synthetic_signal(frame: pd.DataFrame) -> None:
    features = feature_columns(frame.columns, "MedHouseVal")
    train_frame, test_frame = build_splits(frame, test_size=0.2, seed=SEED)

    params = load_params()
    params["model"] = {"name": "linear_regression", "params": {}}
    pipeline = build_pipeline(params)
    pipeline.fit(train_frame[features], train_frame["MedHouseVal"])
    metrics = compute_metrics(test_frame["MedHouseVal"], pipeline.predict(test_frame[features]))

    assert metrics["r2"] > 0.9
    assert metrics["mae"] < 0.2


def test_compute_metrics_reports_r2_and_mae() -> None:
    actual = pd.Series([1.0, 2.0, 3.0])
    metrics = compute_metrics(actual, np.array([1.0, 2.0, 3.0]))
    assert set(metrics) == {"r2", "mae"}
    assert metrics["r2"] == pytest.approx(1.0)
    assert metrics["mae"] == pytest.approx(0.0)


def test_smoke_params_produce_a_cheap_model() -> None:
    smoke = load_params("configs/smoke.yaml")
    model = build_model(smoke["model"], seed=smoke["seed"])
    assert isinstance(model, RandomForestRegressor)
    assert model.n_estimators == 10
    assert smoke["data"]["max_rows"] <= 1000


def test_params_flag_works_before_and_after_the_subcommand() -> None:
    before = parse_args(["--params", "configs/smoke.yaml", "evaluate"])
    after = parse_args(["evaluate", "--params", "configs/smoke.yaml"])

    assert before.params == after.params == "configs/smoke.yaml"
    assert before.command == after.command == "evaluate"


def test_params_default_to_the_root_file() -> None:
    assert parse_args(["train"]).params == "params.yaml"
    assert parse_args(["train", "--force-download"]).force_download is True
