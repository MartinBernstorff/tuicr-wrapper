import json
import os
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from pydantic import BaseModel, RootModel

app = typer.Typer()


class RepoPath(RootModel[str]):
    root: str


class BranchName(RootModel[str]):
    root: str


class CommitHash(RootModel[str]):
    root: str


class ReviewFile(BaseModel):
    reviewed: bool = False


class Review(BaseModel):
    repo_path: str
    branch_name: str
    base_commit: str
    created_at: str = ""
    files: list[ReviewFile] = []

    @property
    def is_completed(self) -> bool:
        return all(f.reviewed for f in self.files)


class GitRepo:
    def __init__(self, path: Path) -> None:
        self.path = path

    def current_branch(self) -> BranchName:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=self.path,
            capture_output=True,
            text=True,
            check=True,
        )
        return BranchName(result.stdout.strip())

    def root(self) -> RepoPath:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=self.path,
            capture_output=True,
            text=True,
            check=True,
        )
        return RepoPath(result.stdout.strip())


def find_reviews(repo_path: RepoPath, branch: BranchName) -> list[Review]:
    reviews_dir = Path.home() / "Library" / "Application Support" / "reviews"
    if not reviews_dir.exists():
        raise FileNotFoundError(f"Reviews directory not found: {reviews_dir}")

    matches = []
    for f in reviews_dir.glob("*.json"):
        data = json.loads(f.read_text())
        review = Review.model_validate(data)
        if review.repo_path == repo_path.root and review.branch_name == branch.root:
            matches.append(review)

    matches.sort(key=lambda r: r.created_at, reverse=True)
    return matches


@app.command()
def main(
    repo_path: Annotated[
        Path | None, typer.Option(help="Path to the git repository")
    ] = None,
) -> None:
    if repo_path is None:
        repo_path = Path.cwd()

    try:
        git = GitRepo(repo_path)
        repo_root = git.root()
        branch = git.current_branch()
    except subprocess.CalledProcessError:
        typer.echo("Error: not a git repository.", err=True)
        raise typer.Exit(1)

    reviews = find_reviews(repo_root, branch)
    if not reviews:
        typer.echo("No reviews found for this branch.")
        raise typer.Exit(1)

    base_commit: CommitHash | None = None
    most_recent = reviews[0]

    if not most_recent.is_completed:
        continue_incomplete = typer.confirm(
            "Most recent review is incomplete. Continue it?", default=True
        )
        if continue_incomplete:
            base_commit = CommitHash(most_recent.base_commit)
        else:
            for review in reviews[1:]:
                if review.is_completed:
                    base_commit = CommitHash(review.base_commit)
                    break
    else:
        base_commit = CommitHash(most_recent.base_commit)

    if not base_commit:
        typer.echo("No completed review found for this branch.")
        raise typer.Exit(1)

    revision_range = f"{base_commit.root}..HEAD"
    typer.echo(f"Opening tuicr with revisions: {revision_range}")
    os.execvp("tuicr", ["tuicr", "--revisions", revision_range])


if __name__ == "__main__":
    app()
