import json
from datetime import datetime
from pathlib import Path

import typer

from incremental_review.git import GitRepo
from incremental_review.models import BranchName, CommitHash, RepoPath, Review

REVIEWS_DIR = Path.home() / "Library" / "Application Support" / "tuicr" / "reviews"


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
