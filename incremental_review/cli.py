import os
from pathlib import Path
from typing import Annotated

import typer

from incremental_review.commands import LaunchTUI, MarkAsReviewed, NoAction, dispatch
from incremental_review.git import GitRepo
from incremental_review.models import IncompleteReview, RevisionRange, TrunkBranch
from incremental_review.review_store import ReviewStore
from incremental_review.settings import load_settings, write_default_settings
from incremental_review.subprocess_runner import Terminal, WorkingDirectory

TRUNK_NAMES = {"develop", "main", "trunk"}

app = typer.Typer()


def launch_tuicr(revision_range: RevisionRange) -> None:
    os.execvp("tuicr", ["tuicr", "--revisions", revision_range.as_arg])


@app.command()
def init(
    repo_path: Annotated[
        Path | None, typer.Option(help="Path to the git repository")
    ] = None,
) -> None:
    """Initialize default incr.toml settings file."""
    working_dir = WorkingDirectory(repo_path or Path.cwd())
    path = write_default_settings(working_dir)
    typer.echo(f"Created default settings at {path}")


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
    settings = load_settings(working_dir)

    if settings.trunk_branch is not None:
        trunk_branch = settings.trunk_branch
    elif branch.root in TRUNK_NAMES:
        trunk_branch = TrunkBranch(branch.root)
    else:
        trunk_input = typer.prompt("Trunk branch name (e.g. main)", default="main")
        trunk_branch = TrunkBranch(trunk_input)

    if not git.branch_exists(trunk_branch):
        typer.echo(f"Error: branch '{trunk_branch.root}' does not exist.", err=True)
        raise typer.Exit(code=1)

    # Don't use trunk fallback when already on trunk
    is_on_trunk = branch.root == trunk_branch.root
    effective_trunk = None if is_on_trunk else trunk_branch

    latest_review = store.find_last_review()

    if isinstance(latest_review, IncompleteReview):
        resume_incomplete = typer.confirm(
            "Most recent review is incomplete. Resume it?", default=True
        )
    else:
        resume_incomplete = False

    last_completed = store.find_last_completed_review()

    if latest_review is None and effective_trunk is None:
        set_current = typer.confirm(
            "No existing reviews found. Mark current commit as reviewed?", default=True
        )
        if not set_current:
            return

    command = dispatch(
        latest_review, last_completed, resume_incomplete, effective_trunk
    )

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
