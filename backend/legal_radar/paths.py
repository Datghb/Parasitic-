"""Resolve project paths in source checkouts and Docker images."""

from pathlib import Path


def repo_root() -> Path:
    """Return the directory containing the project's versioned data."""
    module_path = Path(__file__).resolve()
    for candidate in module_path.parents:
        if (candidate / "data" / "kg" / "kg_nodes.json").is_file():
            return candidate

    # Source-checkout fallback: <repo>/backend/legal_radar/paths.py.
    return module_path.parents[2]


def data_dir() -> Path:
    return repo_root() / "data"


def runs_dir() -> Path:
    return repo_root() / "runs"
