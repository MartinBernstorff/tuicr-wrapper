from dataclasses import dataclass

from incremental_review.models import BranchName, CommitHash, RepoPath
from incremental_review.subprocess_runner import Terminal, WorkingDirectory


@dataclass
class GitRepo:
    path: WorkingDirectory
    terminal: Terminal

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
