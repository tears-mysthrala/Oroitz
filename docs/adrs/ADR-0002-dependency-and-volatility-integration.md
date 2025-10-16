# ADR-0002: Dependency Management and Volatility Integration

## Status

Accepted

## Context

Phase 0 requires selecting a dependency manager for the Python codebase and deciding how to incorporate Volatility 3—either as a vendored submodule or as an external package. We need reproducible environments, support for optional dependency groups (GUI, TUI, docs), and an approach that simplifies updates to Volatility.

## Decision

Use Poetry as the dependency and packaging manager, and depend on the published `volatility3` package via PyPI rather than vendoring the source repository.

## Rationale

- **Poetry Benefits:** Provides deterministic lock files, dependency grouping, and streamlined publishing for future SDK packages.
- **Project Structure Alignment:** `pyproject.toml` consolidates build metadata, dependency declarations, tool configuration (black, ruff), and is already industry standard.
- **Volatility Updates:** Relying on the upstream PyPI package simplifies keeping pace with releases and reduces repository size.
- **Contribution Workflow:** Contributors can install dependencies with a single `poetry install` command, and CI can reuse the same lock file.
- **Extensibility:** Poetry supports optional dependency groups (`dev`, `docs`) matching the needs of GUI/TUI segregation.

## Consequences

- We must maintain a `poetry.lock` file and update it when dependencies change.
- Any patches required for Volatility must be upstreamed or handled via plugin wrappers; vendoring is discouraged unless absolutely necessary (would require new ADR).
- Build pipelines and developer docs must instruct users to install Poetry (or use `pipx` for installation).
