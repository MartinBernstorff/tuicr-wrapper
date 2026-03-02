import os
from pathlib import Path
from typing import Annotated

import typer

from incremental_review.commands import LaunchTUI, MarkAsReviewed, NoAction, dispatch
from incremental_review.git import GitRepo
from incremental_review.models import IncompleteReview, RevisionRange
from incremental_review.review_store import ReviewStore
from incremental_review.settings import (
    SettingsFileAlreadyExists,
    load_settings,
    write_default_settings,
)
from incremental_review.subprocess_runner import Terminal, WorkingDirectory

app = typer.Typer(invoke_without_command=True)


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
    try:
        path = write_default_settings(working_dir)
    except SettingsFileAlreadyExists as e:
        typer.echo(f"Error: settings file already exists at {e}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Created default settings at {path}")


@app.command()
def mark_reviewed() -> None:
    """Mark the current commit as reviewed without launching the TUI."""
    working_dir = WorkingDirectory(Path.cwd())
    git = GitRepo(Terminal(working_dir))
    repo_root = git.root()
    branch = git.current_branch()
    store = ReviewStore(repo_root, branch)
    store.mark_current_commit_as_reviewed(git)
    typer.echo("Current commit marked as reviewed.")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    repo_path: Annotated[
        Path | None, typer.Option(help="Path to the git repository")
    ] = None,
) -> None:
    if ctx.invoked_subcommand is not None:
        return
    working_dir = WorkingDirectory(repo_path or Path.cwd())
    git = GitRepo(Terminal(working_dir))
    repo_root = git.root()
    branch = git.current_branch()
    store = ReviewStore(repo_root, branch)
    settings = load_settings(working_dir)

    if settings.trunk_branch is None:
        typer.echo(
            "No trunk branch configured. Defaulting to 'main'. Consider running 'incr init' to create a settings file, so you can diff against trunk."
        )

    if not git.branch_exists(settings.trunk_branch):
        typer.echo(
            f"Error: settings.trunk_branch '{settings.trunk_branch.root}' does not exist.",
            err=True,
        )
        raise typer.Exit(code=1)

    # Don't use trunk fallback when already on trunk
    is_on_trunk = branch.root == settings.trunk_branch.root
    effective_trunk = None if is_on_trunk else settings.trunk_branch

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
