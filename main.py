import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from pydantic import BaseModel, RootModel

app = typer.Typer()

REVIEWS_DIR = Path.home() / "Library" / "Application Support" / "tuicr" / "reviews"


class RepoPath(RootModel[str]):
    root: str


class BranchName(RootModel[str]):
    root: str


class CommitHash(RootModel[str]):
    root: str


class LineComment(BaseModel):
    id: str
    content: str
    comment_type: str = ""
    created_at: datetime | None = None
    line_context: str | None = None
    side: str | None = None
    line_range: dict[str, int] | None = None


class ReviewFile(BaseModel):
    path: str
    reviewed: bool = False
    status: str = ""
    file_comments: list[str] = []
    line_comments: dict[str, list[LineComment]] = {}


class Review(BaseModel):
    repo_path: RepoPath
    branch_name: BranchName
    base_commit: CommitHash
    created_at: datetime
    files: dict[str, ReviewFile] = {}

    @property
    def is_completed(self) -> bool:
        return all(f.reviewed for f in self.files.values())


@dataclass
class GitRepo:
    path: Path

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

    def current_commit(self) -> CommitHash:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.path,
            capture_output=True,
            text=True,
            check=True,
        )
        return CommitHash(result.stdout.strip())


def find_reviews(repo_path: RepoPath, branch: BranchName) -> list[Review]:
    if not REVIEWS_DIR.exists():
        raise FileNotFoundError(f"Reviews directory not found: {REVIEWS_DIR}")

    matches = []
    for f in REVIEWS_DIR.glob("*.json"):
        data = json.loads(f.read_text())
        review = Review.model_validate(data)
        if review.repo_path == repo_path and review.branch_name == branch:
            matches.append(review)

    matches.sort(key=lambda r: r.created_at, reverse=True)
    return matches


def mark_current_commit_as_reviewed(
    git: GitRepo, repo_root: RepoPath, branch: BranchName
) -> CommitHash:
    REVIEWS_DIR = Path.home() / "Library" / "Application Support" / "reviews"
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)

    commit = git.current_commit()
    review = Review(
        repo_path=repo_root,
        branch_name=branch,
        base_commit=commit,
        created_at=datetime.now(),
        files={},
    )

    review_file = REVIEWS_DIR / f"{commit.root}_{branch.root}.json"
    review_file.write_text(review.model_dump_json(indent=2))
    typer.echo(f"Marked {commit.root} as reviewed.")
    return commit


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
    base_commit: CommitHash | None = None
    if len(reviews) == 0:
        base_commit = None
    else:
        most_recent = reviews[0]

        if most_recent.is_completed:
            base_commit = most_recent.base_commit
        else:
            continue_incomplete = typer.confirm(
                "Most recent review is incomplete. Continue it?", default=True
            )
            if continue_incomplete:
                base_commit = most_recent.base_commit
            else:
                for review in reviews[1:]:
                    if review.is_completed:
                        base_commit = review.base_commit
                        break

    if not base_commit:
        set_current = typer.confirm(
            "No completed review found. Mark current commit as reviewed?", default=True
        )
        if set_current:
            mark_current_commit_as_reviewed(git, repo_root, branch)
            typer.echo(
                "Current commit marked as reviewed. Run again after new changes to start a review."
            )
            raise typer.Exit(0)
        raise typer.Exit(1)

    revision_range = f"{base_commit.root}..HEAD"
    typer.echo(f"Opening tuicr with revisions: {revision_range}")
    os.execvp("tuicr", ["tuicr", "--revisions", revision_range])


if __name__ == "__main__":
    app()
