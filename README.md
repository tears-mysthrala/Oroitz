# Oroitz

Oroitz is a cross-platform wrapper around Volatility 3 that delivers a shared Python core, a Textual-powered TUI, a PySide6 desktop GUI, and a CLI so analysts can run guided memory forensics workflows with minimal setup.

## Overview

- Streamlines common Volatility investigations through a unified, high-level API surface.
- Normalizes plugin outputs into structured formats that downstream tools can consume.
- Shares workflow logic across CLI, GUI, and TUI adapters for consistent analyst experiences.
- Prioritizes extensibility so teams can add custom workflows, post-processors, and output targets.

## Project Status

The repository is in the planning phase; implementation work has not started yet. Architectural goals, workflows, and quality bars are documented under `docs/`. Begin with [`docs/volatility-wrapper-spec.md`](docs/volatility-wrapper-spec.md) for the end-to-end product vision.

## Getting Started

1. Install Python 3.11 and ensure `python --version` reports 3.11.x.
2. Install Poetry per the instructions at <https://python-poetry.org/docs/#installation>.
3. From the repository root, run `poetry install` to create the virtual environment and pull dependencies.
4. Activate the Poetry shell with `poetry shell`, or prefix commands with `poetry run`.
5. Run the placeholder quality checks: `poetry run pytest` for tests and `poetry run ruff check .` for linting once code lands.

Volatility 3 is listed as a dependency in `pyproject.toml`; no additional manual installation is required for local development.

## Planned Repository Layout

- `core/`: Python engine that orchestrates Volatility 3 workflows and normalization.
- `cli/`: Command-line interface that wraps the core engine.
- `ui/gui/`: PySide6 desktop application providing visual workflows.
- `ui/tui/`: Textual-based terminal interface for keyboard-driven investigations.
- `bindings/`: Language-specific SDKs (Python and future Node.js support).
- `tests/`: Automated tests across core, adapters, and interfaces.
- `docs/`: Specifications, ADRs, and contributor-facing guides (see [`docs/project-structure-guide.md`](docs/project-structure-guide.md)).

Refer to [`docs/development-plan.md`](docs/development-plan.md) for the phased roadmap and sequencing strategy.

## Documentation Index

- Product specification: [`docs/volatility-wrapper-spec.md`](docs/volatility-wrapper-spec.md)
- Core engine details: [`docs/core-engine-spec.md`](docs/core-engine-spec.md)
- TUI plan: [`docs/tui-spec.md`](docs/tui-spec.md)
- GUI plan: [`docs/gui-spec.md`](docs/gui-spec.md)
- Workflow catalog: [`docs/workflows-and-plugins.md`](docs/workflows-and-plugins.md)
- Architectural decisions: [`docs/adrs`](docs/adrs)

## Contributing

Contribution guidelines will be published alongside the initial code scaffolding. In the meantime, please file issues or discussion topics to propose ideas, share findings, or coordinate development efforts.

## Security

See [`SECURITY.md`](SECURITY.md) for vulnerability reporting guidance.

## License

This project targets the MIT License; a formal `LICENSE` file will be added before the first code release.
