"""Dataset loading, deterministic materialisation and seeded splitting."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split

from cooked_ml.config import resolve_path

RAW_CSV_NAME = "california_housing.csv"
TARGET = "MedHouseVal"
FLOAT_FORMAT = "%.10g"
DEFAULT_RAW_PATH = Path("data") / "raw" / RAW_CSV_NAME
DEFAULT_CACHE_DIR = Path("data") / "raw" / "sklearn_cache"


def to_frame(bunch: Any) -> pd.DataFrame:
    """Turn a scikit-learn bunch into a DataFrame with a fixed column order."""
    frame = pd.DataFrame(bunch.data, columns=list(bunch.feature_names))
    frame[TARGET] = bunch.target
    return frame[[*bunch.feature_names, TARGET]]


def write_csv(frame: pd.DataFrame, path: Path | str) -> Path:
    """Write a DataFrame to CSV with deterministic bytes.

    Fixed column order, fixed float format and a fixed line terminator so that
    both members get an identical file hash on their own machines.
    """
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(
        destination,
        index=False,
        columns=list(frame.columns),
        float_format=FLOAT_FORMAT,
        lineterminator="\n",
    )
    return destination


def ensure_raw_dataset(
    raw: Path | str | None = None,
    cache: Path | str | None = None,
    *,
    force: bool = False,
) -> Path:
    """Download the California Housing dataset once and cache it as a CSV."""
    destination = Path(raw) if raw is not None else resolve_path(DEFAULT_RAW_PATH)
    if destination.is_file() and not force:
        return destination

    download_cache = Path(cache) if cache is not None else destination.parent / "sklearn_cache"
    download_cache.mkdir(parents=True, exist_ok=True)
    bunch = fetch_california_housing(data_home=str(download_cache))
    return write_csv(to_frame(bunch), destination)


def load_raw(path: Path | str | None = None, max_rows: int | None = None) -> pd.DataFrame:
    """Load the raw CSV and check the columns the pipeline depends on."""
    source = Path(path) if path is not None else resolve_path(DEFAULT_RAW_PATH)
    if not source.is_file():
        raise FileNotFoundError(f"raw dataset not found: {source} (run the train command first)")

    frame = pd.read_csv(source)
    if TARGET not in frame.columns:
        raise ValueError(f"{source} has no target column {TARGET!r}")
    if frame.isna().any().any():
        raise ValueError(f"{source} contains missing values, refusing to train")
    if max_rows is not None:
        frame = frame.head(max_rows)
    return frame


def build_splits(
    frame: pd.DataFrame,
    test_size: float,
    seed: int,
    target: str = TARGET,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split into train/test deterministically from a single seed."""
    if target not in frame.columns:
        raise ValueError(f"target column {target!r} is not in the frame")
    if not 0.0 < test_size < 1.0:
        raise ValueError(f"test_size must be between 0 and 1, got {test_size}")

    train_frame, test_frame = train_test_split(
        frame,
        test_size=test_size,
        random_state=seed,
        shuffle=True,
    )
    return train_frame.sort_index(), test_frame.sort_index()


def save_splits(
    train_frame: pd.DataFrame,
    test_frame: pd.DataFrame,
    out_dir: Path | str,
) -> dict[str, Path]:
    """Persist both splits deterministically, for the DVC pipeline stages."""
    directory = Path(out_dir)
    paths = {
        "train": write_csv(train_frame, directory / "train.csv"),
        "test": write_csv(test_frame, directory / "test.csv"),
    }
    return paths


def file_hash(path: Path | str, algorithm: str = "sha256") -> str:
    """Hash a file so both members can compare their local copies."""
    digest = hashlib.new(algorithm)
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()
