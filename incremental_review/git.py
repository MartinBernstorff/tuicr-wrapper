from dataclasses import dataclass, field
from pathlib import Path

from incremental_review.models import BranchName, CommitHash, RepoPath
from incremental_review.subprocess_runner import SubprocessRunner


@dataclass
class GitRepo:
    path: Path
    runner: SubprocessRunner = field(default_factory=SubprocessRunner)

    def current_branch(self) -> BranchName:
        output = self.runner.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.path
        )
        return BranchName(output)

    def root(self) -> RepoPath:
        output = self.runner.run(
            ["git", "rev-parse", "--show-toplevel"], cwd=self.path
        )
        return RepoPath(output)

    def current_commit(self) -> CommitHash:
        output = self.runner.run(["git", "rev-parse", "HEAD"], cwd=self.path)
        return CommitHash(output)
