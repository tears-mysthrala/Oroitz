# Oroitz

Oroitz is a cross-platform wrapper around Volatility 3 that delivers a shared Python core, a Textual-powered TUI, a PySide6 desktop GUI, and a CLI so analysts can run guided memory forensics workflows with minimal setup.

## Overview

- Streamlines common Volatility investigations through a unified, high-level API surface.
- Normalizes plugin outputs into structured formats that downstream tools can consume.
- Shares workflow logic across CLI, GUI, and TUI adapters for consistent analyst experiences.
- Prioritizes extensibility so teams can add custom workflows, post-processors, and output targets.

## Features

### Core Engine

- Workflow orchestration with plugin execution and result aggregation
- Output normalization and export (JSON, CSV support planned)
- Session management for configuration persistence
- Telemetry and logging infrastructure

### Workflows

- **Quick Triage**: Processes, network connections, and memory analysis
- Extensible workflow registry for custom analysis pipelines

### Interfaces

- **CLI**: Command-line interface with `quick-triage`, `tui`, and `gui` commands
- **GUI**: PySide6-based desktop application with session wizard, dashboard, and results explorer
- **TUI**: Textual-powered terminal interface with interactive workflow selection

### Testing

- Comprehensive unit tests for core components
- UI testing framework setup (GUI tests currently have Qt compatibility issues)
- Mock data fallback for development without real memory images

## Project Status

The repository has progressed from planning to active development with a functional core engine, CLI, GUI, and TUI implementations. The system currently uses mock data for Volatility 3 plugin execution while Volatility integration is being finalized. Core workflows, output normalization, and user interfaces are operational. Refer to [`docs/development-plan.md`](docs/development-plan.md) for the current roadmap and milestones.

## Getting Started

1. Install Python 3.11 and ensure `python --version` reports 3.11.x.
2. Install Poetry per the instructions at <https://python-poetry.org/docs/#installation>.
3. From the repository root, run `poetry install` to create the virtual environment and pull dependencies.
4. Activate the Poetry shell with `poetry shell`, or prefix commands with `poetry run`.
5. Run the quality checks: `poetry run pytest` for tests and `poetry run ruff check .` for linting.

Volatility 3 is listed as a dependency in `pyproject.toml`; no additional manual installation is required for local development.

### Running Oroitz

Once installed, you can run Oroitz in several ways:

- **CLI**: `poetry run python -m oroitz.cli --help` to see available commands
- **GUI**: `poetry run python -m oroitz.ui.gui` to launch the PySide6 desktop application
- **TUI**: `poetry run python -m oroitz.ui.tui` to launch the Textual terminal interface

Example CLI usage:

```bash
# Run quick triage analysis (currently uses mock data)
poetry run python -m oroitz.cli quick-triage /path/to/memory/image.mem --profile Win10x64_19041 --output results.json
```

## Repository Layout

- `oroitz/core/`: Python engine that orchestrates Volatility 3 workflows, output normalization, and session management (currently using mock data)
- `oroitz/cli/`: Command-line interface that wraps the core engine with commands for quick triage and launching UIs
- `oroitz/ui/gui/`: PySide6 desktop application providing visual workflow execution and session management
- `oroitz/ui/tui/`: Textual-based terminal interface for keyboard-driven investigations
- `oroitz/bindings/`: Language-specific SDKs (Python bindings implemented, future Node.js support)
- `tests/`: Automated tests across core, CLI, and UI components
- `docs/`: Specifications, ADRs, and contributor-facing guides

Refer to [`docs/project-structure-guide.md`](docs/project-structure-guide.md) for detailed module organization.

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
