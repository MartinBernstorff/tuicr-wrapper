from polyfactory.factories.pydantic_factory import ModelFactory

from incremental_review.commands import LaunchTUI, MarkAsReviewed, NoAction, dispatch
from incremental_review.models import (
    CompletedReview,
    IncompleteReview,
    Review,
    ReviewFile,
)


class ReviewFactory(ModelFactory):
    __model__ = Review


class TestDispatch:
    def test_completed_review_launches_tuicr(self) -> None:
        existing_review = CompletedReview(
            ReviewFactory.build(files={"a.py": ReviewFile(path="a.py", reviewed=True)})
        )
        result = dispatch(existing_review, None, use_incomplete=False)
        assert isinstance(result, LaunchTUI)
        assert result.revision_range.start == existing_review.root.base_commit

    def test_incomplete_continue_launches_tuicr(self) -> None:
        review = IncompleteReview(
            ReviewFactory.build(files={"a.py": ReviewFile(path="a.py", reviewed=False)})
        )
        result = dispatch(review, None, use_incomplete=True)
        assert isinstance(result, LaunchTUI)
        assert result.revision_range.start == review.root.base_commit

    def test_incomplete_dont_continue_with_completed_fallback(self) -> None:
        incomplete = IncompleteReview(
            ReviewFactory.build(files={"a.py": ReviewFile(path="a.py", reviewed=False)})
        )
        completed = CompletedReview(
            ReviewFactory.build(files={"a.py": ReviewFile(path="a.py", reviewed=True)})
        )

        result = dispatch(incomplete, completed, use_incomplete=False)

        assert isinstance(result, LaunchTUI)
        assert result.revision_range.start == completed.root.base_commit

    def test_incomplete_dont_continue_no_completed(self) -> None:
        review = IncompleteReview(
            ReviewFactory.build(files={"a.py": ReviewFile(path="a.py", reviewed=False)})
        )

        result = dispatch(review, None, use_incomplete=False)

        assert isinstance(result, NoAction)

    def test_none_returns_mark_as_reviewed(self) -> None:
        result = dispatch(None, None, use_incomplete=False)

        assert isinstance(result, MarkAsReviewed)
