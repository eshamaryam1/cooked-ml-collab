"""Command line entry point for the DVC pipeline stages.

    uv run python -m cooked_ml.cli prepare
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

from cooked_ml.config import (
    DEFAULT_PARAMS_PATH,
    artifact_path,
    current_commit_sha,
    dvc_pointer_md5,
    load_params,
    resolve_path,
    set_global_seed,
)
from cooked_ml.data import (
    TARGET,
    build_splits,
    ensure_raw_dataset,
    file_hash,
    load_raw,
    read_splits,
    save_splits,
)
from cooked_ml.features import drop_duplicate_rows, feature_columns
from cooked_ml.models import build_pipeline

GLOBAL_OPTIONS = ("--params", "--data")


def reorder_global_options(argv: list[str]) -> list[str]:
    """Move ``--params`` and ``--data`` in front of the subcommand.

    argparse lets a subparser's defaults overwrite values already parsed by the
    parent, so a flag written after the subcommand would silently fall back to
    ``params.yaml``. Normalising the order keeps both spellings equivalent.
    """
    leading: list[str] = []
    trailing: list[str] = []
    tokens = list(argv)
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in GLOBAL_OPTIONS and index + 1 < len(tokens):
            leading += [token, tokens[index + 1]]
            index += 2
        elif any(token.startswith(f"{option}=") for option in GLOBAL_OPTIONS):
            leading.append(token)
            index += 1
        else:
            trailing.append(token)
            index += 1
    return leading + trailing


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--params",
        default=argparse.SUPPRESS,
        help="parameter file to use (default: params.yaml)",
    )
    common.add_argument("--data", default=argparse.SUPPRESS, help="override the raw CSV path")

    parser = argparse.ArgumentParser(
        prog="cooked_ml", description="California Housing pipeline", parents=[common]
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser(
        "prepare", help="split the raw csv into processed train/test files", parents=[common]
    )
    prepare.add_argument("--force-download", action="store_true", help="re-fetch the raw CSV")

    train = subparsers.add_parser(
        "train", help="fit the model on the processed training split", parents=[common]
    )
    train.add_argument("--force-download", action="store_true", help="re-fetch the raw CSV")

    subparsers.add_parser(
        "evaluate", help="score a saved model and write metrics.json", parents=[common]
    )

    tokens = sys.argv[1:] if argv is None else argv
    args = parser.parse_args(reorder_global_options(tokens))
    if not hasattr(args, "params"):
        args.params = str(DEFAULT_PARAMS_PATH)
    if not hasattr(args, "data"):
        args.data = None
    if not hasattr(args, "force_download"):
        args.force_download = False
    return args


def compute_metrics(y_true: pd.Series | Any, y_pred: Any) -> dict[str, float]:
    """The two metrics the team reports."""
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
    }


def load_frame(params: dict[str, Any], data_path: str | None, force_download: bool) -> pd.DataFrame:
    """Fetch the raw CSV (once) and read the rows the pipeline is allowed to see."""
    raw = Path(data_path) if data_path else resolve_path(params["data"]["raw_path"])
    if force_download and raw.is_file():
        raw.unlink()
    ensure_raw_dataset(raw, resolve_path(params["data"]["cache_dir"]))
    max_rows = params["data"].get("max_rows")
    return load_raw(raw, max_rows=int(max_rows) if max_rows else None)


def run_prepare(
    params: dict[str, Any], data_path: str | None, force_download: bool = False
) -> dict[str, Any]:
    """Raw CSV → optional dedup → seeded split → ``data/processed/*.csv``.

    The preprocessor is deliberately *not* fit here: it is fitted inside the
    train stage's sklearn ``Pipeline``, which only ever sees the training rows.
    """
    frame = load_frame(params, data_path, force_download)
    target = params["data"].get("target", TARGET)

    dropped = 0
    if params["data"].get("drop_duplicates", False):
        before = len(frame)
        frame = drop_duplicate_rows(frame)
        dropped = before - len(frame)

    train_frame, test_frame = build_splits(
        frame,
        test_size=float(params["data"]["test_size"]),
        seed=int(params["seed"]),
        target=target,
    )
    processed_dir = resolve_path(params["data"].get("processed_dir", "data/processed"))
    save_splits(train_frame, test_frame, processed_dir)
    return {
        "rows": int(len(train_frame) + len(test_frame)),
        "n_train": len(train_frame),
        "n_test": len(test_frame),
        "duplicates_dropped": int(dropped),
        "processed_dir": str(processed_dir),
    }


def cmd_prepare(args: argparse.Namespace) -> int:
    params = load_params(args.params)
    set_global_seed(int(params["seed"]))
    print(json.dumps(run_prepare(params, args.data, args.force_download), indent=2))
    return 0


def cmd_train(args: argparse.Namespace) -> int:
    params = load_params(args.params)
    seed = int(params["seed"])
    set_global_seed(seed)
    target = params["data"].get("target", TARGET)
    processed_dir = resolve_path(params["data"].get("processed_dir", "data/processed"))

    if args.force_download or not (processed_dir / "train.csv").is_file():
        run_prepare(params, args.data, args.force_download)

    train_frame, _ = read_splits(processed_dir)
    features = feature_columns(train_frame.columns, target)

    pipeline = build_pipeline(params, seed)
    pipeline.fit(train_frame[features], train_frame[target])

    model_file = artifact_path(params, "model_path")
    model_file.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_file)

    print(
        json.dumps(
            {
                "model": params["model"]["name"],
                "seed": seed,
                "n_train": len(train_frame),
                "model_path": str(model_file),
            },
            indent=2,
        )
    )
    return 0


def load_model(model_file: Path) -> Any:
    """Load a saved pipeline without keeping a private copy of it.

    Scoring only reads the tree arrays, so memory-mapping them lets
    ``evaluate`` run on a machine that is low on commit memory.
    """
    try:
        return joblib.load(model_file, mmap_mode="r")
    except (TypeError, OSError, MemoryError):
        return joblib.load(model_file)


def build_metrics(
    params: dict[str, Any],
    metrics: dict[str, float],
    n_train: int,
    n_test: int,
) -> dict[str, Any]:
    """Provenance for a run, in a fixed key order.

    No timestamp and no other volatile field: two ``dvc repro --force`` runs on
    the same commit must write byte-identical ``metrics.json``, which is the
    Module 06 checkpoint. The module doc's example also carries ``dvc_lock_md5``;
    it is dropped because ``dvc.lock`` is rewritten by the very stage that would
    hash it, so the value changes on every run.
    """
    model_cfg = params["model"]
    model_params = dict(model_cfg.get("params") or {})
    data_cfg = params["data"]
    raw = resolve_path(data_cfg["raw_path"])
    return {
        "r2": metrics["r2"],
        "mae": metrics["mae"],
        "n_train": n_train,
        "n_test": n_test,
        "seed": int(params["seed"]),
        "commit_sha": current_commit_sha(),
        "params": {
            "model": model_cfg.get("name"),
            "n_estimators": model_params.get("n_estimators"),
            "max_depth": model_params.get("max_depth"),
            "min_samples_leaf": model_params.get("min_samples_leaf"),
            "test_size": float(data_cfg["test_size"]),
            "scale": bool(params.get("preprocessing", {}).get("scale", True)),
            "drop_duplicates": bool(data_cfg.get("drop_duplicates", False)),
            "max_rows": data_cfg.get("max_rows"),
        },
        "data": {
            "raw_path": data_cfg["raw_path"],
            "raw_sha256": file_hash(raw),
            "raw_dvc_md5": dvc_pointer_md5(raw),
        },
    }


def cmd_evaluate(args: argparse.Namespace) -> int:
    params = load_params(args.params)
    set_global_seed(int(params["seed"]))
    target = params["data"].get("target", TARGET)

    model_file = artifact_path(params, "model_path")
    if not model_file.is_file():
        raise FileNotFoundError(f"no saved model at {model_file}, run the train command first")

    processed_dir = resolve_path(params["data"].get("processed_dir", "data/processed"))
    train_frame, test_frame = read_splits(processed_dir)
    features = feature_columns(test_frame.columns, target)

    pipeline = load_model(model_file)
    metrics = compute_metrics(test_frame[target], pipeline.predict(test_frame[features]))
    payload = build_metrics(params, metrics, n_train=len(train_frame), n_test=len(test_frame))

    metrics_file = artifact_path(params, "metrics_path")
    # newline="\n": Windows text mode would emit CRLF, and the pre-commit
    # line-ending hook rewrites it to LF afterwards — which would change the
    # md5 DVC recorded for this file and leave `dvc status` permanently dirty.
    # An OSError here (read-only file, path is a directory, disk full) must not
    # escape as a raw traceback: the CLI contract is a clean stderr message.
    try:
        metrics_file.parent.mkdir(parents=True, exist_ok=True)
        metrics_file.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    except OSError as error:
        raise ValueError(f"cannot write {metrics_file}: {error}") from error

    print(json.dumps(payload, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    handlers = {"prepare": cmd_prepare, "train": cmd_train, "evaluate": cmd_evaluate}
    try:
        return handlers[args.command](args)
    except (FileNotFoundError, ValueError, KeyError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except MemoryError:
        print(
            f"error: out of memory while running {args.command}; "
            "close other programs or lower `model.params.n_estimators`, then retry",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
