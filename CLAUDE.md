# CLAUDE.md

## Conventions
- Never return primitives from functions. Use newtypes or pydantic root models instead.

## Verification
* Run type checks: `uv run pyrefly check .`
* Check that the CLI launches