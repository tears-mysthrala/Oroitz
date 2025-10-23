# ADR-0003: Interface Tooling Selection

## Status

Accepted

## Context

The project must offer both a desktop GUI and a terminal-based TUI. We evaluated several options for each interface: Qt (PySide6), Dear PyGui, Kivy, Electron/Tauri for GUI; Textual, Urwid, curses, Blessed for TUI. Tooling should align with the Python core, support modern UX patterns, and remain maintainable.

## Decision

- Adopt PySide6 (Qt for Python) for the GUI implementation.
- Adopt Textual (built on Rich) for the TUI implementation.

## Rationale

- **PySide6:** Provides a mature, cross-platform widget toolkit with designer tooling, theming support, and strong community adoption. It integrates cleanly with Python 3.11 and supports MVVM patterns required by the specification.
- **Textual:** Offers a high-level, reactive framework for terminal apps with rich widgets, CSS theming, and async-friendly architecture. It pairs naturally with the Rich library already planned for structured console output.
- **Shared Language:** Both frameworks are Python-first, enabling shared view models and adapters from the core engine without cross-language shims.
- **Future Proofing:** PySide6 and Textual receive active development and have permissive licenses suitable for open-source collaboration.

## Consequences

- Developers must install Qt runtime dependencies (handled automatically by PySide6 but increases package size).
- The TUI requires terminals with proper Unicode/TrueColor support; legacy terminals may not render optimally.
- Build pipelines must include steps to package the PySide6 application (PyInstaller/Nuitka) and to test Textual apps headlessly.
- Any future switch to alternative frameworks requires new ADRs and potential refactoring of view models.
