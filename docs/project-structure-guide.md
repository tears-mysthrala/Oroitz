# Project Structure Guide

## Purpose

Provide a concrete filesystem layout and setup steps so future contributors can scaffold the repository consistently and without guesswork.

## Directory Layout (Top Level)

- `core/`: Source for the Python orchestration engine that wraps Volatility 3.
- `ui/gui/`: PySide6 desktop application code.
- `ui/tui/`: Textual-based terminal interface code.
- `bindings/`: Language bindings and SDK shims (Python package metadata lives in `bindings/python/`, Node wrapper later in `bindings/node/`).
- `cli/`: Command-line entrypoints that reuse the core engine.
- `docs/`: Project documentation, specifications, ADRs, tutorials.
- `tests/`: Automated tests grouped by component (`tests/core`, `tests/gui`, `tests/tui`, `tests/integration`).
- `assets/`: Shared icons, logos, sample memory images metadata (no large binaries in git).
- `scripts/`: Developer utilities (formatting, linting, release helpers).
- `examples/`: Minimal runnable samples demonstrating SDK, CLI, GUI, and TUI usage.

## Required Top-Level Files

- `pyproject.toml`: Poetry or Hatch config for managing Python dependencies across core, GUI, TUI, and CLI.
- `package.json`: Reserved for future Node binding; include minimal metadata placeholder to avoid confusion.
- `README.md`: High-level overview with quick start instructions.
- `CONTRIBUTING.md`: Contribution guidelines referencing testing commands and release flow.
- `LICENSE`: Choose a permissive license (MIT or Apache-2.0) aligned with community goals.
- `.gitignore`: Cover Python, Qt build artifacts, Textual logs, virtual environments.
- `.editorconfig`: Enforce whitespace and newline conventions.
- `.pre-commit-config.yaml`: Set up formatting (black, ruff, isort) and linting hooks.

## Environment Setup Checklist

1. Install Python 3.11 (exact version) and ensure `python` resolves to it.
2. Install Poetry (or Hatch) for dependency management.
3. Create and activate the virtual environment (`poetry shell`).
4. Run `poetry install` to pull core + GUI/TUI dependencies (PySide6, textual, rich, pydantic, click, etc.).
5. Configure VS Code workspace: enable recommended extensions (Python, Ruff, PySide Designer helper).
6. Confirm Volatility 3 is installed as a dependency or vendored submodule (decide in ADR-0002).
7. Download sample memory images (links only) and store path references in `assets/samples.json` (no binaries in repo).

## Commit Structure Expectations

- Keep commits focused on single subsystems (e.g., "core: add session manager" or "gui: implement triage workflow view").
- Run formatting (`poetry run tox -e fmt` placeholder) and tests (`poetry run tox`) before pushing.
- Reference relevant ADR IDs and issue numbers in commit messages when applicable.

## Build & Run Commands (Placeholder)

- `poetry run vw-cli ...`: Execute CLI (to be implemented).
- `poetry run python -m ui.gui`: Launch GUI bootstrap script.
- `poetry run python -m ui.tui`: Launch TUI bootstrap script.
- `poetry run pytest`: Run full test suite.
- `poetry run tox -e lint`: Run linting suite.

## Future Automation Hooks

- GitHub Actions workflows: `ci.yml` (lint + test), `release.yml` (build & publish packages), `docs.yml` (build docs site).
- Dependabot for Python and GitHub Actions updates.

## Next Steps for Scaffolding

1. Create `pyproject.toml` with shared dependency groups (`core`, `gui`, `tui`, `dev`).
2. Establish namespace packages (`oroitz.core`, `oroitz.gui`, `oroitz.tui`).
3. Add placeholder modules with TODO comments to unblock incremental development.
4. Document any deviations in an ADR and link back to this guide.
