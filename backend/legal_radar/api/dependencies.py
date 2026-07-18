"""Shared FastAPI dependencies."""

from pathlib import Path

from ..paths import data_dir as project_data_dir
from ..paths import repo_root as project_repo_root
from ..paths import runs_dir as project_runs_dir


def repo_root() -> Path:
    return project_repo_root()


def runs_dir() -> Path:
    return project_runs_dir()


def data_dir() -> Path:
    return project_data_dir()
