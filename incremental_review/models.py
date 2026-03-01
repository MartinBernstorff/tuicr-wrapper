import pathlib
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, RootModel


class RepoPath(RootModel[pathlib.Path]): ...


class BranchName(RootModel[str]): ...


class CommitRef(RootModel[str]): ...


class CommitHash(CommitRef): ...


class RevisionRange(BaseModel):
    start: CommitRef
    end: CommitRef = CommitRef("HEAD")

    @property
    def as_arg(self) -> str:
        return f"{self.start.root}..{self.end.root}"


class Comment(BaseModel):
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
    file_comments: list[Comment] = []
    line_comments: dict[str, list[Comment]] = {}


class Review(BaseModel):
    repo_path: RepoPath
    branch_name: BranchName
    base_commit: CommitHash
    created_at: datetime
    files: dict[str, ReviewFile] = {}

    @property
    def is_completed(self) -> bool:
        return all(f.reviewed for f in self.files.values())


class CompletedReview(RootModel[Review]): ...


class IncompleteReview(RootModel[Review]): ...


T = TypeVar("T")


class DateDescending(RootModel[list[T]], Generic[T]):
    """Items sorted by date descending."""
    ...
