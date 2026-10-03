"""Tests for dataset loading, deterministic writing and seeded splitting."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from cooked_ml import data as data_module
from cooked_ml.cli import run_prepare
from cooked_ml.config import load_params
from cooked_ml.data import (
    build_splits,
    ensure_raw_dataset,
    file_hash,
    load_raw,
    read_splits,
    save_splits,
    write_csv,
)
from cooked_ml.features import feature_columns
from cooked_ml.models import build_pipeline

FIXTURE = Path(__file__).parent / "fixtures" / "sample.csv"


@pytest.fixture
def frame() -> pd.DataFrame:
    return load_raw(FIXTURE)


def test_load_raw_returns_expected_columns(frame: pd.DataFrame) -> None:
    assert frame.columns.tolist() == [
        "MedInc",
        "HouseAge",
        "AveRooms",
        "AveBedrms",
        "Population",
        "AveOccup",
        "Latitude",
        "Longitude",
        "MedHouseVal",
    ]
    assert not frame.isna().any().any()


def test_load_raw_rejects_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        load_raw(FIXTURE.with_name("does-not-exist.csv"))


def test_load_raw_rejects_missing_target(tmp_path: Path) -> None:
    broken = tmp_path / "broken.csv"
    broken.write_text("MedInc,HouseAge\n1.0,2.0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="target column"):
        load_raw(broken)


def test_load_raw_max_rows_limits_frame(frame: pd.DataFrame) -> None:
    assert len(load_raw(FIXTURE, max_rows=25)) == 25


def test_write_csv_is_byte_identical_across_calls(frame: pd.DataFrame, tmp_path: Path) -> None:
    first = write_csv(frame, tmp_path / "a.csv")
    second = write_csv(frame, tmp_path / "b.csv")
    assert first.read_bytes() == second.read_bytes()
    assert file_hash(first) == file_hash(second)


def test_write_csv_uses_unix_line_endings(frame: pd.DataFrame, tmp_path: Path) -> None:
    destination = write_csv(frame, tmp_path / "a.csv")
    raw_bytes = destination.read_bytes()
    assert b"\r\n" not in raw_bytes
    assert raw_bytes.endswith(b"\n")


def test_ensure_raw_dataset_skips_download_when_present(tmp_path: Path, monkeypatch) -> None:
    existing = write_csv(
        pd.DataFrame({"MedInc": [1.0], "MedHouseVal": [2.0]}), tmp_path / "raw.csv"
    )

    def explode(*args, **kwargs):
        raise AssertionError("download must not be attempted when the csv exists")

    monkeypatch.setattr(data_module, "fetch_california_housing", explode)
    assert ensure_raw_dataset(existing, tmp_path / "cache") == existing


def test_ensure_raw_dataset_writes_expected_frame(tmp_path: Path, monkeypatch) -> None:
    fake_bunch = SimpleNamespace(
        feature_names=["MedInc", "Latitude"],
        data=[[1.0, 38.0], [2.0, 39.0]],
        target=[0.5, 1.5],
    )

    monkeypatch.setattr(data_module, "fetch_california_housing", lambda data_home: fake_bunch)
    destination = ensure_raw_dataset(tmp_path / "raw.csv", tmp_path / "cache")

    written = pd.read_csv(destination)
    assert written.columns.tolist() == ["MedInc", "Latitude", "MedHouseVal"]
    assert len(written) == 2


def test_build_splits_is_deterministic(frame: pd.DataFrame) -> None:
    first_train, first_test = build_splits(frame, test_size=0.2, seed=42)
    second_train, second_test = build_splits(frame, test_size=0.2, seed=42)

    assert first_train.index.tolist() == second_train.index.tolist()
    assert first_test.index.tolist() == second_test.index.tolist()


def test_build_splits_changes_with_seed(frame: pd.DataFrame) -> None:
    _, test_a = build_splits(frame, test_size=0.2, seed=42)
    _, test_b = build_splits(frame, test_size=0.2, seed=7)
    assert set(test_a.index) != set(test_b.index)


def test_build_splits_partitions_the_frame(frame: pd.DataFrame) -> None:
    train_frame, test_frame = build_splits(frame, test_size=0.2, seed=42)

    assert len(train_frame) == pytest.approx(len(frame) * 0.8, abs=1)
    assert len(test_frame) == pytest.approx(len(frame) * 0.2, abs=1)
    assert set(train_frame.index).isdisjoint(test_frame.index)
    assert len(train_frame) + len(test_frame) == len(frame)


def test_build_splits_rejects_invalid_test_size(frame: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="test_size"):
        build_splits(frame, test_size=1.5, seed=42)


def test_save_splits_round_trips(frame: pd.DataFrame, tmp_path: Path) -> None:
    train_frame, test_frame = build_splits(frame, test_size=0.2, seed=42)
    paths = save_splits(train_frame, test_frame, tmp_path)

    assert load_raw(paths["train"]).shape == train_frame.shape
    assert load_raw(paths["test"]).shape == test_frame.shape


def test_params_file_is_complete() -> None:
    params = load_params()
    for section in ("seed", "data", "model", "preprocessing"):
        assert section in params
    assert 0.0 < params["data"]["test_size"] < 1.0
    assert params["data"]["target"] == "MedHouseVal"
    assert params["data"]["processed_dir"] == "data/processed"
    assert params["data"]["drop_duplicates"] is True


def test_params_smoke_variant_exists() -> None:
    smoke = load_params("configs/smoke.yaml")
    assert smoke["data"]["max_rows"] <= 1000
    assert smoke["model"]["params"]["n_estimators"] < params_baseline_trees()


def params_baseline_trees() -> int:
    return int(load_params()["model"]["params"]["n_estimators"])


def test_scaler_is_fit_on_training_rows_only(frame: pd.DataFrame) -> None:
    """Leakage guard: the scaler must never see the test rows.

    The Module 02 starter scaled the whole dataset before splitting, which
    pushes test statistics into training. The pipeline fits preprocessing
    inside ``Pipeline.fit`` on the training split, so the scaler's stored means
    are the training means and nothing else.
    """
    target = "MedHouseVal"
    features = feature_columns(frame.columns, target)
    train_frame, _ = build_splits(frame, test_size=0.2, seed=42)

    params = load_params()
    params["model"] = {
        "name": "random_forest",
        "params": {"n_estimators": 5, "max_depth": 3, "n_jobs": 1},
    }
    pipeline = build_pipeline(params, seed=42)
    pipeline.fit(train_frame[features], train_frame[target])

    scaler = pipeline.named_steps["preprocess"].named_steps["scale"]
    np.testing.assert_allclose(scaler.mean_, train_frame[features].mean().to_numpy(), rtol=1e-9)
    whole_frame_means = frame[features].mean().to_numpy()
    assert not np.allclose(scaler.mean_, whole_frame_means)


def test_run_prepare_writes_seeded_splits(tmp_path: Path) -> None:
    params = load_params()
    params["data"] = {**params["data"], "processed_dir": str(tmp_path / "processed")}

    first = run_prepare(params, str(FIXTURE))
    first_bytes = (tmp_path / "processed" / "train.csv").read_bytes()
    second = run_prepare(params, str(FIXTURE))
    second_bytes = (tmp_path / "processed" / "train.csv").read_bytes()

    assert first == second
    assert first_bytes == second_bytes
    assert first["n_train"] + first["n_test"] == first["rows"]
    assert (tmp_path / "processed" / "test.csv").is_file()


def test_run_prepare_drops_duplicates_when_asked(tmp_path: Path, frame: pd.DataFrame) -> None:
    source = tmp_path / "raw.csv"
    pd.concat([frame, frame.head(10)], ignore_index=True).to_csv(source, index=False)
    params = load_params()
    params["data"] = {
        **params["data"],
        "processed_dir": str(tmp_path / "processed"),
        "drop_duplicates": True,
    }

    report = run_prepare(params, str(source))

    assert report["duplicates_dropped"] == 10
    assert report["rows"] == len(frame)


def test_read_splits_needs_the_prepare_stage(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="prepare"):
        read_splits(tmp_path)
