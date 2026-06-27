# Contributing to pyduck-ona-viz

Thank you for your interest in making the package better! This document covers
the basics of setting up a development environment, running tests, and
submitting changes.

## Development setup

Clone the repository and install the package in editable mode with all
optional and development dependencies:

```bash
git clone https://github.com/ezraair555/pyduck-ona-viz.git
cd pyduck-ona-viz
python -m pip install -e ".[all,dev]"
```

This installs the visualization backends (matplotlib, networkx, plotly,
pyvis), `pyduck-ona`, and the lint / test / type tools.

## Running tests

The full test suite requires ≥90% line coverage to pass in CI:

```bash
python -m pytest --cov=pyduck_ona_viz --cov-report=term --cov-fail-under=90 tests/
```

To run tests without coverage:

```bash
python -m pytest tests/
```

Slow tests are marked with `@pytest.mark.slow` and skipped by default. Run
them explicitly with:

```bash
python -m pytest -m slow tests/
```

## Linting and formatting

We use `ruff`, `black`, and `isort`. All three must pass before a PR can be
merged:

```bash
python -m ruff check src tests
python -m black --check src tests
python -m isort --check src tests
```

To auto-fix formatting issues:

```bash
python -m black src tests
python -m isort src tests
```

## Type checking

All public and internal functions must be fully type-annotated. Run mypy with:

```bash
python -m mypy src/pyduck_ona_viz
```

Missing imports for optional visualization libraries (plotly, pyvis) are
configured via `[tool.mypy]` in `pyproject.toml`.

## Pre-commit hooks

Install the pre-commit hooks to catch issues before they are committed:

```bash
pre-commit install
pre-commit run --all-files
```

## Pull request expectations

- One logical change per PR.
- Add tests that exercise the new or changed behavior, including edge cases and
  error paths.
- Update docstrings to NumPy style and keep return types in sync with the
  implementation.
- Update `CHANGELOG.md` with a short note under the `[Unreleased]` or upcoming
  version section.
- Make sure CI is green before requesting review.

## Questions?

Open a [discussion](https://github.com/ezraair555/pyduck-ona-viz/discussions)
or email the maintainer at [ezraair555@gmail.com](mailto:ezraair555@gmail.com).
