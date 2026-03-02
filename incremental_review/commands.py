from dataclasses import dataclass

from incremental_review.models import CommitRef, CompletedReview, IncompleteReview, RevisionRange, TrunkBranch


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
    trunk_branch: TrunkBranch | None = None,
) -> Command:
    match last_review:
        case IncompleteReview():
            if use_incomplete:
                return LaunchTUI(RevisionRange(start=last_review.root.base_commit, end=CommitRef("HEAD")))
            if last_completed:
                return LaunchTUI(RevisionRange(start=last_completed.root.base_commit, end=CommitRef("HEAD")))
            return NoAction()
        case CompletedReview():
            return LaunchTUI(RevisionRange(start=last_review.root.base_commit, end=CommitRef("HEAD")))
        case None:
            if trunk_branch is not None:
                return LaunchTUI(RevisionRange(start=CommitRef(trunk_branch.root), end=CommitRef("HEAD")))
            return MarkAsReviewed()
        case _:
            return NoAction()
