import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import typer

from incremental_review.git import GitRepo
from incremental_review.models import (
    BranchName,
    CommitHash,
    CompletedReview,
    DateDescending,
    IncompleteReview,
    RepoPath,
    Review,
)

DEFAULT_REVIEWS_DIR = (
    Path.home() / "Library" / "Application Support" / "tuicr" / "reviews"
)


def _parse_review(path: Path) -> Review:
    data = json.loads(path.read_text())
    return Review.model_validate(data)


@dataclass
class ReviewStore:
    repo_path: RepoPath
    branch: BranchName
    reviews_dir: Path = DEFAULT_REVIEWS_DIR

    def find_reviews(self) -> DateDescending[Review]:
        if not self.reviews_dir.exists():
            raise FileNotFoundError(f"Reviews directory not found: {self.reviews_dir}")

        matches = []
        for f in self.reviews_dir.glob("*.json"):
            review = _parse_review(f)
            if review.repo_path == self.repo_path and review.branch_name == self.branch:
                matches.append(review)

        def _aware(dt: datetime) -> datetime:
            return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt.astimezone(UTC)

        matches.sort(key=lambda r: _aware(r.created_at), reverse=True)
        return DateDescending[Review](matches)

    def find_last_review(self) -> CompletedReview | IncompleteReview | None:
        reviews = self.find_reviews()
        if not reviews.root:
            return None

        most_recent = reviews.root[0]
        if most_recent.is_completed:
            return CompletedReview(most_recent)
        return IncompleteReview(most_recent)

    def find_last_completed_review(self) -> CompletedReview | None:
        reviews = self.find_reviews()
        for review in reviews.root:
            if review.is_completed:
                return CompletedReview(review)
        return None

    def mark_current_commit_as_reviewed(self, git: GitRepo) -> CommitHash:
        self.reviews_dir.mkdir(parents=True, exist_ok=True)

        commit = git.current_commit()
        review = Review(
            repo_path=self.repo_path,
            branch_name=self.branch,
            base_commit=commit,
            created_at=datetime.now(UTC),
            files={},
        )

        review_file = self.reviews_dir / f"{commit.root}_{self.branch.root}.json"
        review_file.write_text(review.model_dump_json(indent=2))
        typer.echo(f"Marked {commit.root} as reviewed.")
        return commit
