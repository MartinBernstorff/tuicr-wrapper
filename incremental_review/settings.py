import tomllib
from pathlib import Path

from pydantic import BaseModel

from incremental_review.models import BranchName
from incremental_review.subprocess_runner import WorkingDirectory


class Settings(BaseModel):
    trunk_branch: BranchName | None = None


def load_settings(working_dir: WorkingDirectory) -> Settings:
    toml_path = working_dir.root / "pyproject.toml"
    if not toml_path.exists():
        return Settings()

    with open(toml_path, "rb") as f:
        data = tomllib.load(f)

    table = data.get("tool", {}).get("incremental-review", {})
    return Settings(**table)
