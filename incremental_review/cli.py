import os
from pathlib import Path
from typing import Annotated

import typer

from incremental_review.git import GitRepo
from incremental_review.models import CompletedReview, IncompleteReview, RevisionRange
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
    git = GitRepo(path=working_dir, terminal=Terminal(cwd=working_dir))
    repo_root = git.root()
    branch = git.current_branch()
    store = ReviewStore(repo_path=repo_root, branch=branch)

    last_review = store.find_last_review()

    match last_review:
        case IncompleteReview():
            if typer.confirm(
                "Most recent review is incomplete. Continue it?", default=True
            ):
                launch_tuicr(RevisionRange(start=last_review.root.base_commit))
                return
            else:
                completed = store.find_last_completed_review()
                if completed:
                    revision_range = RevisionRange(start=completed.root.base_commit)
                    typer.echo(f"Opening tuicr with revisions: {revision_range.as_arg}")
                    launch_tuicr(revision_range)
                    return
        case CompletedReview():
            revision_range = RevisionRange(start=last_review.root.base_commit)
            typer.echo(f"Opening tuicr with revisions: {revision_range.as_arg}")
            launch_tuicr(revision_range)
            return
        case None:
            set_current = typer.confirm(
                "No completed review found. Mark current commit as reviewed?", default=True
            )
            if set_current:
                store.mark_current_commit_as_reviewed(git)
                typer.echo(
                    "Current commit marked as reviewed. Run again after new changes to start a review."
                )
