---
name: python-style
description: >
  Use when writing, reviewing, or refactoring Python code in this project.
  Apply these conventions to all new code and flag violations when reviewing
  existing code. Also activate when the user asks to "check style", "review
  code quality", or "follow project conventions".
---

# Python style guide

Apply these rules to all Python code in this project. For full details on
any section, read ./style-details.md.

## Non-negotiable rules
- All functions and methods must have type hints on parameters and return type
- Use `ruff` for linting — fix all warnings before marking code as done
- No bare `except:` — always catch specific exception types

## Naming
- Variables and functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods/attributes: prefix with single underscore `_name`

## Imports
- Standard library first, then third-party, then local — separated by blank lines
- Use absolute imports; avoid relative imports except within a package
- Never use `import *`

## Functions
- Keep functions focused — one clear responsibility
- Max ~30 lines; if longer, consider splitting
- Prefer pure functions: explicit inputs, explicit outputs, no hidden side effects
- Add a docstring only when the function's purpose or a parameter's intent isn't obvious from its name and type hints alone

## Design
- Isolate mutable state at IO boundaries (event handlers, file writers, Pygame draw calls); keep everything else stateless where possible
- Avoid nesting beyond ~2–3 levels — favour early returns and guard clauses over nested conditionals

## Comments
- Write comments to explain *why* and non-obvious intent, never to describe *what* the code does
- Prefer a well-named variable or function over an explanatory comment
- Delete comments that merely restate the code

## Error handling
- Raise specific exceptions with helpful messages
- Use `pathlib.Path` for all file paths, never `os.path`

## Testing
- Tests live in `tests/` mirroring the source structure
- Use `pytest`; name test functions `test_<what_it_tests>`
- Aim for one assertion per test where practical

## When reviewing code
1. Check for missing type hints first
2. Flag any bare excepts or broad Exception catches
3. Note any functions over ~30 lines or with side effects that could be pure
4. Flag state mutations that leak outside IO boundaries
5. Flag nesting beyond ~2–3 levels; suggest early returns
6. Flag comments that describe *what* the code does rather than *why*
7. Check import ordering
8. Suggest `pathlib` replacements for any `os.path` usage