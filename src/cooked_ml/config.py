"""Configuration loading.

Every tunable value lives in ``params.yaml``; this module only reads and resolves it.
Paths are always resolved relative to the project root, never to an absolute
location on one machine.
"""

from __future__ import annotations

import os
import random
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import yaml

DEFAULT_PARAMS_PATH = Path("params.yaml")
SMOKE_PARAMS_PATH = Path("configs") / "smoke.yaml"


def set_global_seed(seed: int) -> None:
    """Seed every source of randomness a pipeline stage can touch.

    Called first thing by ``prepare``, ``train`` and ``evaluate`` so that a
    rerun replays the same numbers. ``PYTHONHASHSEED`` only affects processes
    started after it is set, so it is recorded here for the next stage and the
    seeded ``random_state`` arguments do the work inside this process.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)


def current_commit_sha() -> str:
    """HEAD of the checkout that produced a run, or ``unknown`` outside Git."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "unknown"


def dvc_pointer_md5(path: Path | str) -> str | None:
    """Read the ``md5`` of the ``.dvc`` pointer that tracks ``path``.

    The raw CSV lives in the DVC remote, so its pointer hash — not a local file
    hash — is what a teammate on a fresh clone can compare against.
    """
    pointer = Path(path)
    if not pointer.is_absolute():
        pointer = resolve_path(pointer)
    dvc_file = Path(f"{pointer}.dvc")
    if not dvc_file.is_file():
        return None
    with dvc_file.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        return None
    outs = payload.get("outs") or [{}]
    value = outs[0].get("md5") or outs[0].get("h")
    return str(value) if value else None


def project_root(start: Path | str | None = None) -> Path:
    """Return the repository root.

    Uses ``start`` when given, otherwise the current directory if it looks like
    the project, and finally the location of this file.
    """
    if start is not None:
        return Path(start).resolve()
    cwd = Path.cwd().resolve()
    if (cwd / "pyproject.toml").is_file():
        return cwd
    return Path(__file__).resolve().parents[2]


def resolve_path(path: Path | str, root: Path | None = None) -> Path:
    """Resolve ``path`` against the project root when it is relative."""
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return (root or project_root()) / candidate


def load_params(path: Path | str = DEFAULT_PARAMS_PATH) -> dict[str, Any]:
    """Read a YAML parameter file and validate the sections the pipeline needs."""
    params_path = resolve_path(path)
    if not params_path.is_file():
        raise FileNotFoundError(f"parameter file not found: {params_path}")

    with params_path.open(encoding="utf-8") as handle:
        params = yaml.safe_load(handle)

    if not isinstance(params, dict):
        raise ValueError(f"{params_path} must contain a YAML mapping at the top level")

    missing = [key for key in ("seed", "data", "model") if key not in params]
    if missing:
        raise ValueError(f"{params_path} is missing required section(s): {missing}")

    return params


def raw_path(params: dict[str, Any]) -> Path:
    return resolve_path(params["data"]["raw_path"])


def cache_dir(params: dict[str, Any]) -> Path:
    return resolve_path(params["data"]["cache_dir"])


def artifact_path(params: dict[str, Any], key: str) -> Path:
    return resolve_path(params.get("artifacts", {}).get(key, f"models/{key}.json"))
