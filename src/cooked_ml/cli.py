"""Command line entry point.

    uv run python -m cooked_ml.cli train
    uv run python -m cooked_ml.cli evaluate

Every value comes from ``params.yaml``; nothing is hardcoded here. Errors are
reported on stderr and turned into a non-zero exit code.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score

from cooked_ml.config import DEFAULT_PARAMS_PATH, artifact_path, load_params, resolve_path
from cooked_ml.data import (
    TARGET,
    build_splits,
    ensure_raw_dataset,
    file_hash,
    load_raw,
)
from cooked_ml.features import feature_columns
from cooked_ml.models import build_pipeline


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="cooked_ml", description="California Housing pipeline")
    parser.add_argument(
        "--params",
        default=str(DEFAULT_PARAMS_PATH),
        help="parameter file to use (default: params.yaml)",
    )
    parser.add_argument("--data", default=None, help="override the raw CSV path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    train = subparsers.add_parser("train", help="fetch data, fit the model and save it")
    train.add_argument("--force-download", action="store_true", help="re-fetch the raw CSV")

    subparsers.add_parser("evaluate", help="score a saved model on the test split")
    return parser.parse_args(argv)


def compute_metrics(y_true: pd.Series | Any, y_pred: Any) -> dict[str, float]:
    """The two metrics the team reports."""
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
    }


def prepare(params: dict[str, Any], data_path: str | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the raw data and split it deterministically."""
    raw = Path(data_path) if data_path else resolve_path(params["data"]["raw_path"])
    max_rows = params["data"].get("max_rows")
    frame = load_raw(raw, max_rows=int(max_rows) if max_rows else None)
    target = params["data"].get("target", TARGET)
    return build_splits(
        frame,
        test_size=float(params["data"]["test_size"]),
        seed=int(params["seed"]),
        target=target,
    )


def cmd_train(args: argparse.Namespace) -> int:
    params = load_params(args.params)
    target = params["data"].get("target", TARGET)

    if args.data:
        raw = Path(args.data)
    else:
        raw = resolve_path(params["data"]["raw_path"])
        if args.force_download and raw.is_file():
            raw.unlink()
    ensure_raw_dataset(raw, resolve_path(params["data"]["cache_dir"]))

    train_frame, test_frame = prepare(params, args.data)
    features = feature_columns(train_frame.columns, target)

    pipeline = build_pipeline(params)
    pipeline.fit(train_frame[features], train_frame[target])

    metrics = compute_metrics(test_frame[target], pipeline.predict(test_frame[features]))

    model_file = artifact_path(params, "model_path")
    model_file.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_file)

    metrics_file = artifact_path(params, "metrics_path")
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    metrics_file.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    report = {
        **metrics,
        "model": params["model"]["name"],
        "seed": int(params["seed"]),
        "rows": int(len(train_frame) + len(test_frame)),
        "test_size": float(params["data"]["test_size"]),
        "data_sha256": file_hash(raw),
        "model_path": str(model_file),
    }
    print(json.dumps(report, indent=2))
    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    params = load_params(args.params)
    target = params["data"].get("target", TARGET)

    model_file = artifact_path(params, "model_path")
    if not model_file.is_file():
        raise FileNotFoundError(f"no saved model at {model_file}, run the train command first")

    train_frame, test_frame = prepare(params, args.data)
    features = feature_columns(test_frame.columns, target)

    pipeline = joblib.load(model_file)
    metrics = compute_metrics(test_frame[target], pipeline.predict(test_frame[features]))
    metrics["model"] = params["model"]["name"]
    metrics["train_rows"] = len(train_frame)
    metrics["test_rows"] = len(test_frame)

    print(json.dumps(metrics, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    handlers = {"train": cmd_train, "evaluate": cmd_evaluate}
    try:
        return handlers[args.command](args)
    except (FileNotFoundError, ValueError, KeyError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
