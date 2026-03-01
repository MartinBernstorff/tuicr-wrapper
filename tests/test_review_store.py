from pathlib import Path
from unittest.mock import MagicMock

from polyfactory.factories.pydantic_factory import ModelFactory

from incremental_review.models import (
    BranchName,
    CommitHash,
    CompletedReview,
    IncompleteReview,
    RepoPath,
    Review,
)
from incremental_review.review_store import ReviewStore


class ReviewFactory(ModelFactory[Review]): ...


class CommitHashFactory(ModelFactory[CommitHash]): ...


def _make_store(tmp_path: Path) -> ReviewStore:
    return ReviewStore(
        RepoPath("/tmp/repo"),
        BranchName("main"),
        reviews_dir=tmp_path,
    )


def test_mark_and_find_last_review(tmp_path: Path) -> None:
    store = _make_store(tmp_path)
    git = MagicMock()
    commit = CommitHash("abc123")
    git.current_commit.return_value = commit

    store.mark_current_commit_as_reviewed(git)

    result = store.find_last_review()
    assert isinstance(result, CompletedReview)
    assert result.root.base_commit == commit


def test_mark_and_find_last_completed_review(tmp_path: Path) -> None:
    store = _make_store(tmp_path)
    git = MagicMock()
    commit = CommitHash("abc123")
    git.current_commit.return_value = commit

    store.mark_current_commit_as_reviewed(git)

    result = store.find_last_completed_review()
    assert isinstance(result, CompletedReview)
    assert result.root.base_commit == commit


def test_incomplete_review_found(tmp_path: Path) -> None:
    store = _make_store(tmp_path)
    git = MagicMock()
    commit = CommitHash("def456")
    git.current_commit.return_value = commit

    store.mark_current_commit_as_reviewed(git)

    # Manually add an unreviewed file to make it incomplete
    review_file = list(tmp_path.glob("*.json"))[0]
    import json

    data = json.loads(review_file.read_text())
    data["files"] = {
        "src/main.py": {
            "path": "src/main.py",
            "reviewed": False,
            "status": "",
            "file_comments": [],
            "line_comments": {},
        }
    }
    review_file.write_text(json.dumps(data))

    result = store.find_last_review()
    assert isinstance(result, IncompleteReview)
    assert result.root.base_commit == commit
