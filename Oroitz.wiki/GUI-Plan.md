# GUI Specification (PySide6)

## Objective

Describe the structure and behavior of the desktop application so it can be implemented consistently by following explicit steps.

## Target Platform

- PySide6 (Qt for Python) for Windows, macOS, and Linux.
- Python 3.11 runtime.
- Bundle later using PyInstaller or Nuitka for distribution.

## Application Structure

- Entrypoint: `ui/gui/main.py` with `main()` launching a `QApplication` and the root `MainWindow` widget.
- Package namespace: `oroitz.gui`.
- Use Qt Designer `.ui` files for core layouts stored in `ui/gui/resources/layouts/`.
- Centralize application state in a `GuiSessionManager` class that wraps core engine sessions.
- Adopt Model-View-ViewModel (MVVM) pattern:
  - View: Qt widgets defined via `.ui` files.
  - ViewModel: Python classes exposing properties/signals to the view.
  - Model: Core engine objects (`Session`, `Workflow`, etc.).

## Primary Windows & Views

1. **Landing View**
   - Purpose: Quick navigation to open/create sessions.
   - Components: Recent sessions list, "New Analysis" button, telemetry opt-in toggle.
   - Actions: Open existing session, launch new session wizard.
2. **New Session Wizard**
   - Step 1: Select memory image (file picker with validation for size, format).
   - Step 2: Choose profile (dropdown populated from core engine helper).
   - Step 3: Select workflow (radio buttons with description and estimated runtime).
   - Step 4: Review summary and optional advanced settings (concurrency, cache enable, telemetry opt-in).
3. **Session Dashboard**
   - Layout: Split view with workflow progress on the left, result tabs on the right.
   - Widgets: Progress timeline, status badges, plugin logs accordion.
   - Actions: Start/pause/resume workflow, view event log, export results.
4. **Results Explorer**
   - Tabs per data artifact (Processes, Network, DLLs, Timeline).
   - Each tab includes table view with filtering/search, export buttons (JSON/CSV/Parquet), and contextual help pane.
   - Provide summary stats cards (counts, anomalies flagged).
5. **Settings Dialog**
   - Sections: General, Paths, Telemetry, Advanced.
   - Bindings: Update config via core engine `config` module and persist.

## Navigation Flow

- Landing View → New Session Wizard → Session Dashboard.
- Session Dashboard may open Results Explorer in stacked tabs.
- Settings Dialog accessible from menu bar and global shortcut (`Ctrl+,`).
- Error modals surface blocking issues; non-blocking warnings appear in notification toast area.

## Visual Design

- Adopt dark theme by default with optional light theme toggle.
- Use consistent spacing (8 px base grid) and typography (Qt default fonts).
- Icons stored under `ui/gui/resources/icons/` in SVG format.
- Provide high-contrast palette for accessibility; expose theme switch inside settings.

## State Management

- Introduce `GuiStore` singleton using Qt signals/slots to broadcast state changes (session updates, workflow progress, result availability).
- Subscribe views to relevant signals to update UI reactively.
- Keep long-running work off the main thread; use `QThreadPool` + `QRunnable` or `asyncio` integration to prevent UI freeze.

## Integration with Core Engine

- GUI uses `oroitz.core` session API via an adapter layer `oroitz.gui.adapters.core_adapter`.
- Adapter exposes async-friendly methods returning futures/promises to integrate with UI threads.
- Progress events from the core engine map to Qt signals displayed in progress timeline and logs panes.

## Error & Notification Handling

- Use a centralized `NotificationCenter` to queue success, info, warning, and error toasts.
- For fatal errors, display modal dialog with summary, details expander, and copy-to-clipboard support.
- Log errors to UI-specific logger (`logs/gui.log`) in addition to core logs.

## Accessibility Requirements

- All interactive elements reachable via keyboard; define tab order explicitly.
- Provide tooltip or status bar descriptions for icons-only buttons.
- Ensure color choices meet WCAG AA contrast ratios.
- Offer text scaling setting (90%, 100%, 110%, 125%).

## Internationalization Hooks

- Wrap user-facing strings with Qt translation (`QtCore.QCoreApplication.translate`).
- Store translation files under `ui/gui/i18n/` (initially only English, but structure ready for more).

## Testing Strategy

- Unit tests: Use `pytest-qt` for signal/slot assertions and widget behavior.
- Integration tests: Launch the main window in headless mode, run through wizard flows via `QTest` events.
- Snapshot tests: Capture key widgets using `pytest-qt` screenshot fixtures for regression detection.
- Manual test script: Checklist covering navigation, theme switching, file dialogs, exports.

## Implementation Checklist

1. Scaffold `oroitz.gui` package with `__init__.py`, `main.py`, `adapters/`, `viewmodels/`, `views/`, `resources/`.
2. Create base `MainWindow` derived from `QMainWindow` with menu bar and stacked central widget.
3. Implement Landing View layout in Qt Designer; connect signals for session selection.
4. Build New Session Wizard as `QWizard` subclass with validation hooks calling core adapter.
5. Implement Session Dashboard with progress view, logs pane, and results tab placeholder.
6. Integrate Result Explorer tables using `QTableView` + custom `QAbstractTableModel` pulling from normalized data.
7. Add Settings Dialog with forms bound to configuration models and persistence.
8. Wire NotificationCenter and GUI store to core engine events; ensure thread-safe updates.
9. Add theme management, icon loading, and translation scaffolding.
10. Write initial automated tests and document manual testing steps.
