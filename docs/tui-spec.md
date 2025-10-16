# TUI Specification (Textual)

## Objective

Define how to implement the terminal user interface using Textual so developers can follow a deterministic script.

## Target Platform

- Python 3.11.
- Textual (latest stable) with Rich backend.
- Support standard ANSI-compatible terminals on Windows Terminal, macOS Terminal/iTerm2, and Linux shells.

## Application Structure

- Entrypoint: `ui/tui/app.py` with `VolWrapTUI(App)` subclass.
- Package namespace: `volwrap.tui`.
- Organize code into `views/`, `widgets/`, `controllers/`, `services/` directories.
- Use Textual `Message` classes for event propagation between components.
- Maintain shared state in `TuiSessionStore` (simple dataclass + notifier pattern).

## Core Views

1. **HomeView**
   - Lists recent sessions, quick actions (new session, resume session, open settings).
   - Displays system status (Volatility installed, cache size, telemetry state).
2. **SessionWizardView**
   - Stepper layout using `Horizontal`/`Vertical` containers.
   - Steps: image selection (path input + validation), profile selection (table), workflow selection (list with details panel), confirmation.
3. **RunView**
   - Layout: top status bar, middle area with plugin progress list, bottom log panel.
   - Shows progress for each plugin, estimated time remaining, ability to pause/cancel.
4. **ResultsView**
   - Tabbed interface using `Tabs` widget (Processes, Network, DLLs, Timeline).
   - Each tab uses `DataTable` with filtering commands (`/filter process chrome`).
   - Provide export commands surfaced in command palette.
5. **SettingsView**
   - Forms for general/options, cache management, telemetry, advanced toggles.
   - Buttons to clear cache, open config file in external editor.

## Navigation & Command Palette

- Global command palette triggered with `Ctrl+K` / `Cmd+K`.
- Provide commands: `new`, `open`, `settings`, `help`, `pause`, `resume`, `export`.
- Breadcrumb component at top indicates current view and session state.
- Support keyboard shortcuts: `F5` run/pause, `F6` resume, `Esc` back, `Ctrl+S` save session metadata.

## Styling Guidelines

- Use Textual CSS files stored in `ui/tui/styles/`.
- Base theme derived from Monokai with adjustments for accessibility.
- Highlight active widgets with bold borders; avoid relying solely on color.
- Provide high-contrast mode toggle in settings.

## Integration with Core Engine

- Use async API: wrap core engine calls in `asyncio` tasks via `run_worker` helper.
- Subscribe to core engine event stream; map to Textual messages (`PluginStarted`, `PluginProgress`, `PluginCompleted`).
- Cache results in store and render tables lazily to keep UI responsive.

## Error Handling

- Display non-blocking alerts in status bar with details accessible via command palette (`show errors`).
- For fatal errors, switch to dedicated Error screen with guidance and "copy details" action.
- Log TUI-specific traces to `logs/tui.log`.

## Accessibility Considerations

- Provide full keyboard navigation; document key bindings in help overlay.
- Support screen readers by emitting descriptive text (Textual supports accessible text via `aria_label` equivalents).
- Allow users to increase font size via settings (apply to CSS variables).

## Testing Strategy

- Unit tests: Validate message handling, store updates, and command handlers.
- Snapshot tests: Render key views with `textual-testing` utilities and compare textual output.
- Integration tests: Use Textual pilot framework to simulate user input flows (create session, run workflow, export).
- Manual script: Validate terminal compatibility (Windows, macOS, Linux) and color contrast.

## Implementation Checklist

1. Scaffold `volwrap.tui` package with base `App` subclass, `views`, and `widgets` directories.
2. Implement `TuiSessionStore` with observable pattern to notify views of updates.
3. Build `HomeView` with recent sessions table and command palette shortcuts.
4. Implement `SessionWizardView` stepper, leveraging validation helpers from core engine.
5. Create `RunView` progress layout; wire to core engine events for live updates.
6. Implement `ResultsView` with `DataTable` components and filtering commands.
7. Add `SettingsView` with forms bound to configuration models.
8. Integrate command palette and global keyboard shortcuts.
9. Hook up error handling overlay and logging.
10. Add CSS themes plus high-contrast variant.
11. Write automated tests and document manual verification steps.
