from dataclasses import dataclass
from subprocess import CalledProcessError

from incremental_review.models import BranchName, CommitHash, RepoPath, TrunkBranch
from incremental_review.subprocess_runner import Terminal


class NotAGitRepo(Exception):
    pass


@dataclass
class GitRepo:
    terminal: Terminal

    def __post_init__(self) -> None:
        try:
            self.terminal.run_quietly(["git", "rev-parse", "--git-dir"])
        except CalledProcessError:
            raise NotAGitRepo(f"{self.terminal.cwd.root} is not a git repository")

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

    def branch_exists(self, branch: BranchName) -> bool:
        try:
            self.terminal.run_quietly(
                ["git", "rev-parse", "--verify", branch.root]
            )
            return True
        except CalledProcessError:
            return False

    def current_commit(self) -> CommitHash:
        output = self.terminal.run_quietly(["git", "rev-parse", "HEAD"])
        return CommitHash(output.root)
