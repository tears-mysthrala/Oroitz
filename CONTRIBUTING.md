# Contributing to Oroitz

Thank you for considering a contribution. This project aims to build a cross-platform wrapper around Volatility 3 with shared core logic and multiple user interfaces. Please review the guidance below before opening issues or pull requests.

## Ground Rules

- Align proposals and implementations with the specifications under `docs/`, starting with [`docs/volatility-wrapper-spec.md`](docs/volatility-wrapper-spec.md) and the companion component specs.
- Treat architecture decision records in `docs/adrs/` as authoritative unless a new ADR is proposed.
- Keep business logic within the `oroitz.core` package and use adapters for CLI, GUI, and TUI layers.
- Follow the code style enforced by Ruff and Black; avoid introducing additional formatters without discussion.
- Do not commit large memory images or proprietary Volatility plugins; reference public datasets instead.

## Getting Started

1. Install Python 3.11 or 3.12 (3.11 recommended for maximum compatibility) and Poetry.
2. Run `poetry install` to create and populate the virtual environment.
3. Activate the environment using `poetry shell` or prefix commands with `poetry run`.
4. Copy `.env.example` files if they exist for the subsystem you are touching (none yet).

## Development Workflow

- Create feature branches from `main` and keep the scope focused.
- Update or author tests alongside code changes. Unit tests belong under `tests/`, mirroring the package structure.
- Run `poetry run pytest` and `poetry run ruff check .` before submitting a pull request.
- Document behavioral or API changes in the relevant markdown files under `docs/`.
- Coordinate significant architectural shifts or new dependencies via GitHub Discussions before implementation.

## Pull Request Checklist

- [ ] Tests cover new and affected code paths.
- [ ] Linting passes locally (`poetry run ruff check .`).
- [ ] Documentation updates accompany behavior changes.
- [ ] Commit messages reference related issues or ADRs where applicable.
- [ ] Security-impacting changes include a threat assessment or note in the PR description.

## Reporting Issues

- Use GitHub Issues for bugs, feature requests, and documentation updates.
- Provide reproduction steps, logs, or screenshots when reporting problems.
- For security-related findings, follow the process outlined in [`SECURITY.md`](SECURITY.md).
