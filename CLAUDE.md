# CLAUDE.md

## Conventions
- Never return primitives from functions. Use newtypes or pydantic root models instead.
- RootModel bodies should be `...` (ellipsis), not explicit field declarations.

## Verification
* Run type checks: `uv run pyrefly check .`
* Check that the CLI launches