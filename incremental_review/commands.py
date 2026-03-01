from dataclasses import dataclass

from incremental_review.models import CompletedReview, IncompleteReview, RevisionRange


@dataclass(frozen=True)
class LaunchTUI:
    revision_range: RevisionRange


@dataclass(frozen=True)
class MarkAsReviewed:
    pass


@dataclass(frozen=True)
class NoAction:
    pass


Command = LaunchTUI | MarkAsReviewed | NoAction


def dispatch(
    last_review: CompletedReview | IncompleteReview | None,
    last_completed: CompletedReview | None,
    use_incomplete: bool,
) -> Command:
    match last_review:
        case IncompleteReview():
            if use_incomplete:
                return LaunchTUI(RevisionRange(start=last_review.root.base_commit))
            if last_completed:
                return LaunchTUI(RevisionRange(start=last_completed.root.base_commit))
            return NoAction()
        case CompletedReview():
            return LaunchTUI(RevisionRange(start=last_review.root.base_commit))
        case None:
            return MarkAsReviewed()
        case _:
            return NoAction()
