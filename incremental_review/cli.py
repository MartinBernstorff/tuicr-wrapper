import os
from pathlib import Path
from typing import Annotated

import typer

from incremental_review.git import GitRepo
from incremental_review.models import CommitHash
from incremental_review.review_store import (
    find_reviews,
    mark_current_commit_as_reviewed,
)

app = typer.Typer()


@app.command()
def main(
    repo_path: Annotated[
        Path | None, typer.Option(help="Path to the git repository")
    ] = None,
) -> None:
    if repo_path is None:
        repo_path = Path.cwd()

    git = GitRepo(repo_path)
    repo_root = git.root()
    branch = git.current_branch()

    reviews = find_reviews(repo_root, branch)

    base_commit: CommitHash | None = None

    if not len(reviews) == 0:
        most_recent = reviews[0]

        if not most_recent.is_completed:
            if not typer.confirm(
                "Most recent review is incomplete. Continue it?", default=True
            ):
                for review in reviews[1:]:
                    if review.is_completed:
                        base_commit = review.base_commit
                        break
            base_commit = most_recent.base_commit

    if not base_commit:
        set_current = typer.confirm(
            "No completed review found. Mark current commit as reviewed?", default=True
        )
        if set_current:
            mark_current_commit_as_reviewed(git, repo_root, branch)
            typer.echo(
                "Current commit marked as reviewed. Run again after new changes to start a review."
            )
        raise typer.Exit(1)

    if base_commit.root == git.current_commit().root:
        launch_anyway = typer.confirm(
            "No new changes since last reviewed commit. Would you like to review ?",
            default=False,
        )
        if not launch_anyway:
            raise typer.Exit(0)
        revision_range = "HEAD~1..HEAD"
    else:
        revision_range = f"{base_commit.root}..HEAD"
    typer.echo(f"Opening tuicr with revisions: {revision_range}")
    os.execvp("tuicr", ["tuicr", "--revisions", revision_range])
