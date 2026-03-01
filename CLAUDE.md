# CLAUDE.md

## Conventions
- Never use primitives. Use newtypes or pydantic root models instead.
- RootModel bodies should be `...` (ellipsis), not explicit field declarations.

## Testing
- Use `polyfactory` (`ModelFactory[T]`) to build test fixtures for pydantic models instead of hand-written helper functions.

## Verification
* Run type checks: `uv run pyrefly check .`
* Run tests: `uv run pytest`
* Check that the CLI launches
