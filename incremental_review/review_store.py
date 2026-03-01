import json
from datetime import datetime
from pathlib import Path

import typer

from incremental_review.git import GitRepo
from incremental_review.models import (
    BranchName,
    CommitHash,
    CompletedReview,
    IncompleteReview,
    RepoPath,
    Review,
    SortedReviews,
)

REVIEWS_DIR = Path.home() / "Library" / "Application Support" / "tuicr" / "reviews"


def _parse_review(path: Path) -> Review:
    data = json.loads(path.read_text())
    return Review.model_validate(data)


def find_reviews(repo_path: RepoPath, branch: BranchName) -> SortedReviews:
    if not REVIEWS_DIR.exists():
        raise FileNotFoundError(f"Reviews directory not found: {REVIEWS_DIR}")

    matches = []
    for f in REVIEWS_DIR.glob("*.json"):
        review = _parse_review(f)
        if review.repo_path == repo_path and review.branch_name == branch:
            matches.append(review)

    matches.sort(key=lambda r: r.created_at, reverse=True)
    return SortedReviews(matches)


def find_last_review(
    repo_path: RepoPath, branch: BranchName
) -> CompletedReview | IncompleteReview | None:
    reviews = find_reviews(repo_path, branch)
    if not reviews.root:
        return None

    most_recent = reviews.root[0]
    if most_recent.is_completed:
        return CompletedReview(most_recent)
    return IncompleteReview(most_recent)


def find_last_completed_review(
    repo_path: RepoPath, branch: BranchName
) -> CompletedReview | None:
    reviews = find_reviews(repo_path, branch)
    for review in reviews.root:
        if review.is_completed:
            return CompletedReview(review)
    return None


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
