import os
from pathlib import Path
from typing import Annotated

import typer

from incremental_review.git import GitRepo
from incremental_review.models import CommitHash, RevisionRange
from incremental_review.review_store import (
    find_reviews,
    mark_current_commit_as_reviewed,
)

app = typer.Typer()


def launch_tuicr(revision_range: RevisionRange) -> None:
    os.execvp("tuicr", ["tuicr", "--revisions", revision_range.root])


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

    last_completed_review: CommitHash | None = None

    if not len(reviews) == 0:
        most_recent = reviews[0]

        if not most_recent.is_completed:
            if typer.confirm(
                "Most recent review is incomplete. Continue it?", default=True
            ):
                launch_tuicr(RevisionRange(f"{most_recent.base_commit.root}..HEAD"))
            else:
                for review in reviews[1:]:
                    if review.is_completed:
                        last_completed_review = review.base_commit
                        break

    if not last_completed_review:
        set_current = typer.confirm(
            "No completed review found. Mark current commit as reviewed?", default=True
        )
        if set_current:
            mark_current_commit_as_reviewed(git, repo_root, branch)
            typer.echo(
                "Current commit marked as reviewed. Run again after new changes to start a review."
            )
        raise typer.Exit(1)

    revision_range = RevisionRange(f"{last_completed_review.root}..HEAD")
    typer.echo(f"Opening tuicr with revisions: {revision_range.root}")
    launch_tuicr(revision_range)
