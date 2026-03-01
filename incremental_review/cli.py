import os
from pathlib import Path
from typing import Annotated

import typer

from incremental_review.commands import LaunchTUI, MarkAsReviewed, NoAction, dispatch
from incremental_review.git import GitRepo
from incremental_review.models import IncompleteReview, RevisionRange
from incremental_review.review_store import ReviewStore
from incremental_review.subprocess_runner import Terminal, WorkingDirectory

app = typer.Typer()


def launch_tuicr(revision_range: RevisionRange) -> None:
    os.execvp("tuicr", ["tuicr", "--revisions", revision_range.as_arg])


@app.command()
def main(
    repo_path: Annotated[
        Path | None, typer.Option(help="Path to the git repository")
    ] = None,
) -> None:
    working_dir = WorkingDirectory(repo_path or Path.cwd())
    git = GitRepo(Terminal(working_dir))
    repo_root = git.root()
    branch = git.current_branch()
    store = ReviewStore(repo_root, branch)

    latest_review = store.find_last_review()

    resume_incomplete = False
    if isinstance(latest_review, IncompleteReview):
        resume_incomplete = typer.confirm(
            "Most recent review is incomplete. Resume it?", default=True
        )

    last_completed = store.find_last_completed_review()

    if latest_review is None:
        set_current = typer.confirm(
            "No existing reviews found. Mark current commit as reviewed?", default=True
        )
        if not set_current:
            return

    command = dispatch(latest_review, last_completed, resume_incomplete)

    match command:
        case LaunchTUI(revision_range=rr):
            typer.echo(f"Opening tuicr with revisions: {rr.as_arg}")
            launch_tuicr(rr)
        case MarkAsReviewed():
            store.mark_current_commit_as_reviewed(git)
            typer.echo(
                "Current commit marked as reviewed. Run again after new changes to start a review."
            )
        case NoAction():
            pass
