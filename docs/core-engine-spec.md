# Core Engine Specification

## Scope

Define the architecture, data flow, and responsibilities of the Python-based engine that orchestrates Volatility 3 operations and feeds both the GUI and TUI interfaces.

## Guiding Principles

- Keep business logic in the core so the CLI, GUI, and TUI remain thin.
- Ensure deterministic behavior: given the same inputs, the engine produces identical outputs.
- Prefer composition over inheritance; rely on dependency injection to simplify testing.

## Module Breakdown

- `volwrap.core.session`
  - Manages lifecycle of analysis sessions (create, load, save, resume).
  - Tracks metadata (image path, profile, plugin versions, timestamps).
  - Provides context manager support for resource cleanup.
- `volwrap.core.workflow`
  - Defines reusable workflows as ordered plugin operations and transforms.
  - Validates plugin compatibility with the supplied memory image profile.
  - Exposes registry functions (`register`, `get`, `list`) with schema validation.
- `volwrap.core.executor`
  - Wraps Volatility 3 plugin invocation.
  - Handles concurrency configuration, timeouts, retries.
  - Emits structured events for logging/telemetry.
- `volwrap.core.output`
  - Normalizes plugin output to structured models using Pydantic.
  - Supports exporters for JSON, CSV, Parquet, and in-memory pandas DataFrames.
  - Provides streaming writers for large outputs.
- `volwrap.core.cache`
  - Persists intermediate results keyed by session + plugin parameters.
  - Supports pluggable backends (filesystem default; future SQLite/Redis adapters).
- `volwrap.core.config`
  - Loads and validates configuration from files (`config.toml`), environment variables, CLI flags, or UI bindings.
  - Supplies typed settings objects to other modules.
- `volwrap.core.telemetry`
  - Emits structured logs, metrics, and optional analytics events.
  - Integrates with the GUI/TUI to display progress and errors.

## Data Flow Overview

1. Caller creates a `Session` with memory image metadata and optional configuration overrides.
2. Caller selects a workflow (`quick_triage`, `process_deepdive`, etc.).
3. `Workflow` resolves the ordered list of Volatility plugins plus transformations.
4. `Executor` runs each plugin, streaming outputs through the `Output` module.
5. Results are cached and normalized; GUI/TUI subscribe to progress events.
6. Final results are returned to the caller and optionally exported.

## Key Classes (Informal Interfaces)

- `Session`
  - Properties: `id`, `image_path`, `profile`, `config`, `state` (`initialized`, `running`, `completed`, `failed`).
  - Methods: `run(workflow_name, options)`, `get_results(format, filters=None)`, `export(destination, format, filters=None)`, `close()`.
- `Workflow`
  - Properties: `name`, `description`, `steps` (plugins + transforms), `required_artifacts`.
  - Methods: `execute(session, executor, output_adapter)`, `validate(profile)`.
- `Executor`
  - Methods: `run_plugin(session, plugin_name, plugin_args)`, `emit_event(event)`.
  - Events: `PluginStarted`, `PluginCompleted`, `PluginFailed`, `ProgressUpdated`.
- `OutputAdapter`
  - Methods: `ingest(plugin_name, raw_data)`, `finalize()`, `export(format, destination, filters)`.

## Configuration Strategy

- Default config file: `config/default.toml`.
- User overrides stored in `~/.volwrap/config.toml` (Windows path equivalent on win32).
- Session-specific overrides passed via CLI/UI serialized into the session record.
- Validation performed with Pydantic models; fail fast with descriptive errors.

## Error Handling Rules

- Differentiate between recoverable plugin errors and fatal session errors.
- Provide actionable messages (missing symbols, unsupported profile, corrupted image).
- Surface errors to GUI/TUI via event bus; display remediation suggestions drawn from knowledge base.
- Log full stack traces to rotating file logs (`logs/volwrap.log`).

## Telemetry & Logging

- Default logging: structured JSON logs with severity, session id, plugin, message.
- Optional telemetry: anonymized metrics (workflow name, duration, success/failure) gated by opt-in flag.
- Provide `TelemetrySink` interface to allow GUI/TUI to attach live dashboards.

## Concurrency Model

- Use Python `asyncio` for orchestrating plugin execution when Volatility supports async hooks; otherwise run plugins in worker processes via `concurrent.futures.ProcessPoolExecutor`.
- Limit parallelism via configuration (`config.core.max_workers`).
- Ensure thread-safe access to caches and output writers.

## Volatility Integration

- Treat Volatility 3 as an external dependency imported into the core.
- Wrap plugin invocation to capture stdout/stderr and convert into structured data.
- Provide compatibility layer to handle changes in Volatility plugin signatures.

## Persistence Artifacts

- Session metadata stored as JSON in `~/.volwrap/sessions/{session_id}.json`.
- Cached plugin outputs stored under `~/.volwrap/cache/{session_id}/{plugin_name}/` with metadata manifest.
- Exported artifacts go to user-specified directories; include provenance file describing inputs and Volatility versions.

## Testing Guidelines

- Unit tests: mock Volatility calls; verify workflow validation and output normalization.
- Integration tests: run against small public memory images with limited plugins (pslist, netscan) to keep CI under time limits.
- Property-based tests for schema validation to ensure consistent output structures.
- Benchmark harness to record processing time and memory usage for core workflows.

## Implementation Order (Recommended)

1. Build configuration and logging backbone.
2. Implement `Session` and session persistence.
3. Add workflow registry with two seed workflows (`quick_triage`, `process_deepdive`).
4. Implement executor with event emission and plugin stubs.
5. Add output normalization + export paths.
6. Integrate cache layer and finalize telemetry hooks.
7. Expose API bindings for CLI/GUI/TUI consumption.
