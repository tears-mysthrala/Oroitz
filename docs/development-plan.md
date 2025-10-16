# Development Plan

## Goal

Provide an execution order with concrete tasks so implementation can proceed phase-by-phase without ambiguity.

## Phase 0 – Preparation

1. Review all specification documents (`volatility-wrapper-spec.md`, `project-structure-guide.md`, `core-engine-spec.md`, `gui-spec.md`, `tui-spec.md`, `workflows-and-plugins.md`).
2. Decide on dependency manager (Poetry recommended) and create `pyproject.toml` with stub packages.
3. Author Architecture Decision Records:
   - ADR-0001 Language & Runtime (Python primary).
   - ADR-0002 Dependency management & Volatility integration approach (submodule vs pip).
   - ADR-0003 Interface tooling (PySide6 + Textual).
4. Initialize Git repository (if not already) and configure pre-commit hooks.

## Phase 1 – Core Foundation

1. Scaffold repository structure (see Project Structure Guide).
2. Implement configuration system (`oroitz.core.config`) with default + user overrides.
3. Add logging/telemetry scaffolding.
4. Create session model and persistence layer (no Volatility calls yet).
5. Write unit tests for configuration and session persistence.

## Phase 2 – Workflow & Volatility Integration

1. Implement workflow registry and seed workflows from catalogue.
2. Integrate Volatility 3 execution via `oroitz.core.executor` with plugin stubs.
3. Implement output normalization and schema validation for `quick_triage` data.
4. Add caching layer for plugin results.
5. Provide CLI prototype commands to run `quick_triage` for testing.
6. Expand unit/integration tests to cover `quick_triage` end-to-end (mock small dataset if needed).

## Phase 3 – TUI (Baseline)

1. Scaffold Textual application structure.
2. Implement HomeView, SessionWizardView, and RunView connected to core engine.
3. Add ResultsView with DataTable exports for `quick_triage` outputs.
4. Wire command palette, shortcuts, and error handling overlays.
5. Write automated tests (Textual pilot) for create-run-export flow.
6. Collect manual testing feedback; adjust UX issues.

## Phase 4 – GUI (Beta)

1. Scaffold PySide6 application with MainWindow and Landing View.
2. Implement New Session Wizard and integrate with core session creation.
3. Build Session Dashboard showing workflow progress and logs.
4. Implement Results Explorer with table filtering and export actions.
5. Add Settings dialog, notification center, and theming support.
6. Write pytest-qt integration tests covering wizard and dashboard flows.
7. Gather usability feedback and iterate on layout.

## Phase 5 – Feature Expansion

1. Add remaining workflows (`process_deepdive`, `network_focus`, `timeline_overview`).
2. Enhance output normalization schemas and export options (Parquet, DataFrame).
3. Implement telemetry opt-in flows and analytics sink.
4. Improve caching (optional SQLite backend) and concurrency settings.
5. Add Node.js binding stub (if required for roadmap).

## Phase 6 – Hardening & Release Prep

1. Conduct performance benchmarking using large sample memory images.
2. Complete documentation site with step-by-step guides and screenshots.
3. Finalize installer packaging (PyInstaller) and create distribution artifacts.
4. Prepare release checklist and CI/CD workflows.
5. Run security review (dependency scan, threat model summary).
6. Tag release candidate and gather community feedback.

## Continuous Activities

- Maintain ADRs when architectural decisions change.
- Keep tests green; enforce via CI on every pull request.
- Update roadmap documents after each milestone.
- Log retrospective notes to improve process.
