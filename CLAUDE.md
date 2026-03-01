# CLAUDE.md

## Conventions
- Never return primitives from functions. Use newtypes or pydantic root models instead.
- RootModel bodies should be `...` (ellipsis), not explicit field declarations.

## Testing
- Use `polyfactory` (`ModelFactory`) to build test fixtures for pydantic models instead of hand-written helper functions.

## Verification
* Run type checks: `uv run pyrefly check .`
* Check that the CLI launches