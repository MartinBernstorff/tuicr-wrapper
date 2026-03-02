from pathlib import Path

import tomli_w
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, TomlConfigSettingsSource

from incremental_review.models import TrunkBranch
from incremental_review.subprocess_runner import WorkingDirectory

SETTINGS_FILENAME = "incr.toml"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file=SETTINGS_FILENAME)

    trunk_branch: TrunkBranch = TrunkBranch("main")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls, deep_merge=True),)


def load_settings(working_dir: WorkingDirectory) -> Settings:
    toml_path = working_dir.root / SETTINGS_FILENAME
    if not toml_path.exists():
        return Settings()
    source = TomlConfigSettingsSource(Settings, toml_file=toml_path)
    return Settings(_build_sources=((source,), {}))


class SettingsFileAlreadyExists(Exception):
    pass


def write_default_settings(working_dir: WorkingDirectory) -> Path:
    toml_path = working_dir.root / SETTINGS_FILENAME

    if toml_path.exists():
        raise SettingsFileAlreadyExists(str(toml_path))

    defaults = Settings().model_dump(mode="json", exclude_none=True)
    with open(toml_path, "wb") as f:
        tomli_w.dump(defaults, f)

    return toml_path
