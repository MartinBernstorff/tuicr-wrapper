import tomllib
from pathlib import Path

import pytest

from incremental_review.settings import (
    SETTINGS_FILENAME,
    Settings,
    SettingsFileAlreadyExists,
    write_default_settings,
)
from incremental_review.subprocess_runner import WorkingDirectory


def test_write_default_settings_creates_file(tmp_path: Path) -> None:
    wd = WorkingDirectory(tmp_path)
    result = write_default_settings(wd)

    assert result.exists()
    with open(result, "rb") as f:
        data = tomllib.load(f)

    defaults = Settings().model_dump(mode="json", exclude_none=True)
    assert data == defaults


def test_write_default_settings_errors_if_file_exists(tmp_path: Path) -> None:
    wd = WorkingDirectory(tmp_path)
    (tmp_path / SETTINGS_FILENAME).write_text('trunk_branch = "develop"\n')

    with pytest.raises(SettingsFileAlreadyExists):
        write_default_settings(wd)
