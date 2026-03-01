import subprocess
from dataclasses import dataclass
from pathlib import Path

from pydantic import RootModel


class TerminalOutput(RootModel[str]):
    root: str


class WorkingDirectory(RootModel[Path]):
    root: Path


@dataclass
class Terminal:
    cwd: WorkingDirectory

    def run_quietly(self, args: list[str]) -> TerminalOutput:
        result = subprocess.run(
            args,
            cwd=self.cwd.root,
            capture_output=True,
            text=True,
            check=True,
        )
        return TerminalOutput(result.stdout.strip())
