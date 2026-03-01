import json
import os
import subprocess
import sys
from pathlib import Path

import typer

app = typer.Typer()


def get_current_branch(repo_path: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_repo_root(repo_path: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def is_review_completed(review: dict) -> bool:
    files = review.get("files", [])
    return all(f.get("reviewed", False) for f in files)


def find_reviews(repo_path: str, branch: str) -> list[dict]:
    reviews_dir = Path.home() / "Library" / "Application Support" / "reviews"
    if not reviews_dir.exists():
        return []

    matches = []
    for f in reviews_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("repo_path") == repo_path and data.get("branch_name") == branch:
            matches.append(data)

    matches.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return matches


@app.command()
def main(
    repo_path: Path = typer.Option(None, help="Path to the git repository"),
) -> None:
    if repo_path is None:
        repo_path = Path.cwd()

    try:
        repo_root = get_repo_root(repo_path)
        branch = get_current_branch(repo_path)
    except subprocess.CalledProcessError:
        typer.echo("Error: not a git repository.", err=True)
        raise typer.Exit(1)

    reviews = find_reviews(repo_root, branch)
    if not reviews:
        typer.echo("No reviews found for this branch.")
        raise typer.Exit(1)

    base_commit = None
    most_recent = reviews[0]

    if not is_review_completed(most_recent):
        continue_incomplete = typer.confirm(
            "Most recent review is incomplete. Continue it?", default=True
        )
        if continue_incomplete:
            base_commit = most_recent.get("base_commit")
        else:
            for review in reviews[1:]:
                if is_review_completed(review):
                    base_commit = review.get("base_commit")
                    break
    else:
        base_commit = most_recent.get("base_commit")

    if not base_commit:
        typer.echo("No completed review found for this branch.")
        raise typer.Exit(1)

    revision_range = f"{base_commit}..HEAD"
    typer.echo(f"Opening tuicr with revisions: {revision_range}")
    os.execvp("tuicr", ["tuicr", "--revisions", revision_range])


if __name__ == "__main__":
    app()
