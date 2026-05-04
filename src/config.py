"""Centrale config-loader. Eén bron van waarheid voor paths, dates, hyperparams."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def load_config(path: Path | str | None = None) -> dict[str, Any]:
    """Load project config from YAML.

    Parameters
    ----------
    path : Path | str | None
        Override default config path. If None, loads `config.yaml` from project root.

    Returns
    -------
    dict
        Parsed config tree.
    """
    cfg_path = Path(path) if path else CONFIG_PATH
    with cfg_path.open("r") as f:
        return yaml.safe_load(f)


def resolve_path(relative: str) -> Path:
    """Resolve a config-relative path to an absolute path under PROJECT_ROOT."""
    return (PROJECT_ROOT / relative).resolve()


CONFIG = load_config()
