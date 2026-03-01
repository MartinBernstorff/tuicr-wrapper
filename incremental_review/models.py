import pathlib
from datetime import datetime

from pydantic import BaseModel, RootModel


class RepoPath(RootModel[pathlib.Path]): ...


class BranchName(RootModel[str]):
    root: str


class CommitHash(RootModel[str]):
    root: str


class RevisionRange(BaseModel):
    start: CommitHash
    end: str = "HEAD"

    @property
    def as_arg(self) -> str:
        return f"{self.start.root}..{self.end}"


class LineComment(BaseModel):
    id: str
    content: str
    comment_type: str = ""
    created_at: datetime | None = None
    line_context: str | None = None
    side: str | None = None
    line_range: dict[str, int] | None = None


class ReviewFile(BaseModel):
    path: str
    reviewed: bool = False
    status: str = ""
    file_comments: list[str] = []
    line_comments: dict[str, list[LineComment]] = {}


class Review(BaseModel):
    repo_path: RepoPath
    branch_name: BranchName
    base_commit: CommitHash
    created_at: datetime
    files: dict[str, ReviewFile] = {}

    @property
    def is_completed(self) -> bool:
        return all(f.reviewed for f in self.files.values())


class CompletedReview(RootModel[Review]):
    root: Review


class IncompleteReview(RootModel[Review]):
    root: Review


class SortedReviews(RootModel[list[Review]]):
    """Reviews sorted by created_at descending."""

    root: list[Review]
