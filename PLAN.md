Context                                                                                                                                                                                    
                                                                                                                                                                                            
 The cli.py main function mixes decision logic (what to do) with side effects (typer.confirm, launch_tuicr, echo). Extract a pure dispatcher that returns command objects, making the logic 
  testable without mocking IO.                                                                                                                                                              

 Approach

 1. Define command types in a new incremental_review/commands.py

 Union of dataclasses representing each possible action:
 - LaunchTuicr(revision_range: RevisionRange, message: str | None) — launch tuicr
 - MarkAsReviewed — mark current commit reviewed
 - NoAction — nothing to do

 Use a union type: Command = LaunchTuicr | MarkAsReviewed | NoAction

 2. Create dispatcher function in incremental_review/commands.py

 def dispatch(last_review: CompletedReview | IncompleteReview | None, continue_incomplete: bool) -> Command
 Pure function: takes the last review state + user's yes/no choice for the incomplete prompt, returns a Command. For the None case (no review found), returns MarkAsReviewed.

 Note: The incomplete review case has two sub-paths (continue vs. fall back to last completed). The dispatcher needs last_completed_review as well for the fallback path. So signature:

 def dispatch(
     last_review: CompletedReview | IncompleteReview | None,
     last_completed: CompletedReview | None,
     continue_incomplete: bool,
 ) -> Command

 3. Simplify cli.py to: gather state → call dispatcher → execute command

 The main() function becomes:
 1. Build git/store objects (same as now)
 2. Fetch last_review and last_completed
 3. If incomplete review, prompt user → continue_incomplete
 4. If no review, prompt user → if no, return
 5. Call dispatch(...) → get command
 6. Match on command and execute side effects

 4. Add tests in tests/test_commands.py

 Test each dispatch path:
 - Completed review → LaunchTuicr
 - Incomplete + continue → LaunchTuicr with incomplete's commit
 - Incomplete + don't continue + has completed → LaunchTuicr with completed's commit
 - Incomplete + don't continue + no completed → NoAction
 - None → MarkAsReviewed

 Files modified

 - incremental_review/commands.py (new)
 - incremental_review/cli.py (simplified)
 - tests/test_commands.py (new)

 Verification

 - uv run pyrefly check .
 - uv run pytest tests/ -v