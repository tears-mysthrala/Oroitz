# Oroitz

Oroitz is a cross-platform wrapper around Volatility 3 that delivers a shared Python core, a Textual-powered TUI, a PySide6 desktop GUI, and a CLI so analysts can run guided memory forensics workflows with minimal setup.

## Overview

Oroitz delivers a complete, production-ready memory forensics platform built on Volatility 3:

- **Unified API**: Streamlines common Volatility investigations through a consistent, high-level interface
- **Multi-Interface**: Choose between CLI, GUI, or TUI based on your workflow preferences
- **Real Execution**: Direct integration with Volatility 3 CLI for authentic memory analysis
- **Auto-Detection**: Automatic symbol table detection eliminates manual profile configuration
- **Structured Output**: Normalized plugin outputs in JSON/CSV formats for downstream analysis
- **Extensible**: Plugin architecture supports custom workflows and output processors

## Features

### Core Engine

- **Real Volatility 3 Integration**: Direct CLI execution with automatic symbol table detection
- **Workflow Orchestration**: Plugin execution, result aggregation, and error handling
- **Output Normalization**: Structured JSON/CSV export with schema validation
- **Session Management**: Configuration persistence and analysis history
- **Caching System**: Performance optimization for repeated analyses
- **Telemetry & Logging**: Comprehensive observability and debugging

### Workflows

- **Quick Triage**: Complete process, network, and memory analysis suite
- **Extensible Registry**: Plugin architecture for custom analysis pipelines

### Interfaces

- **CLI**: Full-featured command-line interface with JSON/CSV export
- **GUI**: Polished PySide6 desktop application with visual workflow management
- **TUI**: Keyboard-driven Textual interface for terminal-based analysis

### Testing & Quality

- **Comprehensive Test Suite**: 53 passing tests covering all components
- **Real Memory Samples**: Included forensic samples for integration testing
- **Real Memory Samples**: Not included in the repository due to size and privacy constraints. Use `assets/samples.json` and the helper script `scripts/fetch_samples.py` to download approved sample images into a local `samples/` directory for integration testing. See `samples/README.md` for details.
- **Mock Data Fallback**: Graceful degradation when Volatility 3 unavailable
- **Code Quality**: Ruff linting and Black formatting enforced

## Project Status

Oroitz is a fully functional cross-platform Volatility 3 wrapper with complete CLI, GUI, and TUI interfaces. The system uses real Volatility 3 execution with automatic symbol table detection, comprehensive testing, and production-ready documentation. All core workflows are operational with proper output normalization and export capabilities.

## Development Roadmap

See [ROADMAP.md](ROADMAP.md) for the complete development roadmap and progress tracking.

## Getting Started

1. Install Python 3.11 and ensure `python --version` reports 3.11.x.
2. Install Poetry per the instructions at <https://python-poetry.org/docs/#installation>.
3. From the repository root, run `poetry install` to create the virtual environment and pull dependencies.
4. Activate the Poetry shell with `poetry shell`, or prefix commands with `poetry run`.
5. Run the quality checks: `poetry run pytest` for tests and `poetry run ruff check .` for linting.

Volatility 3 is listed as a dependency in `pyproject.toml`; no additional manual installation is required for local development. Representative memory images are not committed to this repository because they are large and may contain sensitive data. To obtain approved test samples, use `assets/samples.json` together with the helper script `scripts/fetch_samples.py` which will download verified samples into the local `samples/` directory. See `samples/README.md` for instructions and licensing/provenance guidance. The system automatically detects symbol tables from memory images — no manual profile configuration needed.

### Running Oroitz

Once installed, you can run Oroitz in several ways:

- **CLI**: `poetry run python -m oroitz.cli --help` to see available commands
- **GUI**: `poetry run python -m oroitz.ui.gui` to launch the PySide6 desktop application
- **TUI**: `poetry run python -m oroitz.ui.tui` to launch the Textual terminal interface

Example CLI usage:

```bash
# Run quick triage analysis (Volatility 3 auto-detects symbol tables)
poetry run python -m oroitz.cli quick-triage /path/to/memory/image.mem --output results.json

# Test with a real memory sample (example)
# 1) Fetch an approved sample into the local samples/ directory (example uses a small, CI-friendly sample):
#    python scripts/fetch_samples.py --id samsclass-memdump
#    # If the sample is an archive (e.g. .7z), extract it to produce the memory image file.
# 2) Run quick-triage against the downloaded sample:
poetry run python -m oroitz.cli quick-triage samples/windows-sample-memory.dmp --output real-results.json

# Or fetch and use the Linux sample image (if available locally):
#    python scripts/fetch_samples.py --id volatility-win7-sp1-x64
poetry run python -m oroitz.cli quick-triage samples/linux-sample-memory.bin --output real-results-linux.json
```

### Building and Packaging

Oroitz can be packaged as standalone executables for distribution using PyInstaller. The build system creates platform-specific executables for CLI, GUI, and TUI interfaces.

#### Local Building

**On Windows:**

```powershell
# Install dependencies and build
.\build.ps1 install
.\build.ps1 build

# Or run full release build
.\build.ps1 release
```

**On Linux/macOS:**

```bash
# Install dependencies and build
make install
make build

# Or run full release build
make release
```

Built executables will be placed in the `dist/` directory.

#### Automated Releases

When a version tag (e.g., `v1.0.0`) is pushed, GitHub Actions automatically builds executables for Windows, macOS, and Linux, then creates a GitHub release with downloadable archives.

## Repository Layout

- `oroitz/core/`: Python engine that orchestrates Volatility 3 workflows, output normalization, and session management (real Volatility 3 execution with automatic symbol table detection)
- `oroitz/cli/`: Command-line interface that wraps the core engine with commands for quick triage and launching UIs
- `oroitz/ui/gui/`: PySide6 desktop application providing visual workflow execution and session management
- `oroitz/ui/tui/`: Textual-based terminal interface for keyboard-driven investigations
- `oroitz/bindings/`: Language-specific SDKs (Python bindings implemented, future Node.js support)
- `samples/`: Local directory intended to hold representative memory images for integration testing. Large images are not committed to the repository; use `scripts/fetch_samples.py` with `assets/samples.json` to populate this directory with approved samples. See `samples/README.md` for more information and legal/licensing notes.
- `tests/`: Automated tests across core, CLI, and UI components
- `docs/`: Specifications, ADRs, and contributor-facing guides (available on [GitHub Wiki](https://github.com/tears-mysthrala/Oroitz/wiki))

Refer to [Project Structure Guide](https://github.com/tears-mysthrala/Oroitz/wiki/Project-Structure-Guide) for detailed module organization.

Refer to [Development Plan](https://github.com/tears-mysthrala/Oroitz/wiki/Development-Plan) for the phased roadmap and sequencing strategy.

## Documentation Index

### User Guides

- [Getting Started](https://github.com/tears-mysthrala/Oroitz/wiki/Getting-Started) - Installation and first analysis
- [CLI User Guide](https://github.com/tears-mysthrala/Oroitz/wiki/CLI-Guide) - Command-line interface usage
- [GUI User Guide](https://github.com/tears-mysthrala/Oroitz/wiki/GUI-Guide) - Desktop application tutorial
- [TUI User Guide](https://github.com/tears-mysthrala/Oroitz/wiki/TUI-Guide) - Terminal interface guide
- [Workflow Reference](https://github.com/tears-mysthrala/Oroitz/wiki/Workflow-Reference) - Complete workflow documentation
- [Troubleshooting](https://github.com/tears-mysthrala/Oroitz/wiki/Troubleshooting) - Common issues and solutions

### Technical Documentation

- [Product specification](https://github.com/tears-mysthrala/Oroitz/wiki/Product-Specification)
- [Core engine details](https://github.com/tears-mysthrala/Oroitz/wiki/Core-Engine-Details)
- [TUI plan](https://github.com/tears-mysthrala/Oroitz/wiki/TUI-Plan)
- [GUI plan](https://github.com/tears-mysthrala/Oroitz/wiki/GUI-Plan)
- [Workflow catalog](https://github.com/tears-mysthrala/Oroitz/wiki/Workflow-Catalog)
- [Architectural decisions](https://github.com/tears-mysthrala/Oroitz/wiki/ADR-0001-Language-and-Runtime)
- [Project structure guide](https://github.com/tears-mysthrala/Oroitz/wiki/Project-Structure-Guide)
- [Development plan](https://github.com/tears-mysthrala/Oroitz/wiki/Development-Plan)

## Contributing

Contribution guidelines will be published alongside the initial code scaffolding. In the meantime, please file issues or discussion topics to propose ideas, share findings, or coordinate development efforts.

## Security

See [`SECURITY.md`](SECURITY.md) for vulnerability reporting guidance.

## License

This project targets the MIT License; a formal `LICENSE` file will be added before the first code release.

## Release Prep & CI

We maintain a CI pipeline at `.github/workflows/ci.yml` which runs the test suite and a lightweight benchmark. Use `tools/benchmark.py` to run a local benchmark and generate `results/benchmark_report.json`.

Before releasing, consult the [Release Checklist](https://github.com/tears-mysthrala/Oroitz/wiki/Release-Checklist) for validation steps (benchmarks, SBOM, packaging, security scan, and docs checks).
