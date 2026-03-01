import subprocess
from pathlib import Path


class SubprocessRunner:
    def run(self, args: list[str], cwd: Path) -> str:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
