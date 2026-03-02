import pathlib
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, RootModel


class RepoPath(RootModel[pathlib.Path]): ...


class BranchName(RootModel[str]): ...


class TrunkBranch(BranchName): ...


class CommitRef(RootModel[str]): ...


class CommitHash(CommitRef): ...


class RevisionRange(BaseModel):
    start: CommitRef
    end: CommitRef

    @property
    def as_arg(self) -> str:
        return f"{self.start.root}..{self.end.root}"


class CommentId(RootModel[str]): ...


class CommentContent(RootModel[str]): ...


class CommentType(RootModel[str]): ...


class LineContext(RootModel[str]): ...


class Side(RootModel[str]): ...


class LineRange(RootModel[dict[str, int]]): ...


class FilePath(RootModel[str]): ...


class FileStatus(RootModel[str]): ...


class Comment(BaseModel):
    id: CommentId
    content: CommentContent
    comment_type: CommentType = CommentType("")
    created_at: datetime | None = None
    line_context: LineContext | None = None
    side: Side | None = None
    line_range: LineRange | None = None


class ReviewFile(BaseModel):
    path: FilePath
    reviewed: bool = False
    status: FileStatus = FileStatus("")
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
