# ADR-0001: Language and Runtime Selection

## Status

Accepted

## Context

The project aims to build a wrapper around Volatility 3 that powers both GUI (desktop) and TUI (terminal) interfaces. Volatility 3 itself is implemented in Python and exposes APIs that are most readily consumed from Python code. We require a language that integrates seamlessly with Volatility, supports rich GUI/TUI frameworks, and is accessible to the DFIR community contributing to the wrapper.

## Decision

Adopt Python 3.11 as the primary implementation language and runtime across the core engine, CLI, GUI, and TUI components.

## Rationale

- **Compatibility:** Python is the native language of Volatility 3, eliminating FFI overhead and reducing integration risk.
- **Ecosystem:** Mature libraries exist for both PySide6 (GUI) and Textual (TUI), aligned with the product goals.
- **Contributor Familiarity:** DFIR practitioners and security engineers are more likely to be comfortable with Python, improving maintainability.
- **Tooling:** Python 3.11 offers performance improvements (e.g., adaptive interpreter) and long-term support, balancing stability and modern features.
- **Testing Infrastructure:** Python-first tooling (pytest, pytest-qt, textual testing) simplifies automated testing.

## Consequences

- All contributors need Python 3.11 installed; downstream toolchains must support this version.
- Performance-critical sections may still require optimization; future ADRs can introduce Rust/C extensions behind narrow interfaces if justified.
- Language bindings for other ecosystems (Node.js) will wrap the Python core rather than reimplement logic elsewhere.
