# ADR-0004: Retry & Fallback Policy for Volatility CLI Execution

Status: Accepted

## Context
Volatility 3 execution may fail transiently (e.g., timeouts, temporary OS resource constraints) or be unavailable in some environments (CI, developer machine). Phase 6 requires hardening and predictable behavior across environments.

## Decision
We will add a configurable retry/backoff policy for invoking the Volatility 3 CLI and a clear fallback behavior to mock outputs when persistent problems occur or the CLI is not available:

- Default retry attempts: 2
- Default backoff: 1.0s (exponential backoff multiplier)
- If retries are exhausted or Volatility CLI not present, use a deterministic mock fallback and mark results with a `used_mock` flag.
- Emit `attempts` metadata with each plugin execution to aid debugging and telemetry.

## Consequences
- Positive: Improved reliability in the presence of transient upstream failure and predictable CI behavior.
- Negative: Mock fallback masks real analysis; this behavior should only be used for offline developer workflows and CI; production users must be warned.

## Implementation notes
- Configurable via `Config` (`volatility_retry_attempts`, `volatility_retry_backoff_seconds`).
- ExecutionResult includes `attempts` and `used_mock` fields.
- UI/TUI surfaces attempt counts and fallback notifications in logs.
- Telemetry emits retry events; telemetry can be disabled via existing config.


"