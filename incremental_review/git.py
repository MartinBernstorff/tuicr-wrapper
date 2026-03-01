from dataclasses import dataclass, field

from incremental_review.models import BranchName, CommitHash, RepoPath
from incremental_review.subprocess_runner import Terminal, WorkingDirectory


@dataclass
class GitRepo:
    path: WorkingDirectory
    terminal: Terminal = field(init=False)

    def __post_init__(self) -> None:
        self.terminal = Terminal(cwd=self.path)

    def current_branch(self) -> BranchName:
        output = self.terminal.run_quietly(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        )
        return BranchName(output.root)

    def root(self) -> RepoPath:
        output = self.terminal.run_quietly(
            ["git", "rev-parse", "--show-toplevel"]
        )
        return RepoPath(output.root)

    def current_commit(self) -> CommitHash:
        output = self.terminal.run_quietly(["git", "rev-parse", "HEAD"])
        return CommitHash(output.root)
