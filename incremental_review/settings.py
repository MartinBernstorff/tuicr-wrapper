import tomllib
from pathlib import Path

from pydantic import BaseModel

from incremental_review.models import TrunkBranch
from incremental_review.subprocess_runner import WorkingDirectory

SETTINGS_FILENAME = "incr.toml"


class Settings(BaseModel):
    trunk_branch: TrunkBranch | None = None


def load_settings(working_dir: WorkingDirectory) -> Settings:
    toml_path = working_dir.root / SETTINGS_FILENAME
    if not toml_path.exists():
        return Settings()

    with open(toml_path, "rb") as f:
        data = tomllib.load(f)

    return Settings(**data)


def write_default_settings(working_dir: WorkingDirectory) -> Path:
    toml_path = working_dir.root / SETTINGS_FILENAME
    toml_path.write_text('# trunk_branch = "main"\n')
    return toml_path
