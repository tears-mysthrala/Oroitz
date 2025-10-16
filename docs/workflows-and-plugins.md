# Workflows and Plugin Definitions

## Purpose

Document the default workflows, their constituent Volatility plugins, expected outputs, and validation rules so implementers know exactly what to wire up.

## Workflow Naming Convention

- Use snake_case identifiers (e.g., `quick_triage`).
- Provide human-readable labels and descriptions for GUI/TUI display.
- Maintain workflow metadata in `core/workflows/catalog.json` (to be created).

## Workflow Catalogue (Initial Release)

### quick_triage

- **Goal:** Rapid overview of running processes, network connections, and suspicious memory regions.
- **Plugins (in order):**
  1. `windows.pslist`
  2. `windows.netscan`
  3. `windows.malfind`
- **Transforms:**
  - Normalize timestamps to ISO 8601.
  - Tag processes by prevalence using embedded knowledge base.
- **Outputs:**
  - `processes` table (PID, name, path, start time, anomalies).
  - `network_connections` table (protocol, local/remote addresses, state).
  - `malfind_hits` table (process, address, signature score).
- **Success Criteria:** All plugins return without fatal error; anomalies flagged count available.
- **UI Expectations:**
  - GUI: Progress bar per plugin, summary cards (process count, flagged processes, open ports).
  - TUI: Progress list, ability to drill into flagged processes via command `show process <pid>`.

### process_deepdive

- **Goal:** Provide exhaustive process tree analysis including DLL listings and handles.
- **Plugins:**
  1. `windows.pstree`
  2. `windows.dlllist`
  3. `windows.handles`
  4. `windows.psscan`
- **Transforms:**
  - Build parent-child tree representation.
  - Merge DLL version data from PE metadata.
- **Outputs:**
  - `process_tree` hierarchical data for visualization.
  - `dll_inventory` table (process, dll_name, path, signing status).
  - `handles` table (process, type, name, access rights).
- **UI Expectations:**
  - GUI: Tree view with collapsible nodes, side panel for DLL details, export buttons.
  - TUI: Tree printed using Rich tree widget, commands `expand`, `collapse`, `filter dll <term>`.

### network_focus

- **Goal:** Highlight network activity, sockets, and associated processes.
- **Plugins:**
  1. `windows.netscan`
  2. `windows.sockscan`
  3. `windows.connections`
- **Transforms:**
  - Consolidate socket entries into unified schema.
  - Enrich with geolocation (optional future feature; stub now).
- **Outputs:**
  - `network_connections` table with aggregated data.
  - `suspicious_connections` list flagged by heuristics (e.g., rare ports, known bad IPs).
- **UI Expectations:**
  - GUI: Map widget placeholder (future), highlight suspicious rows.
  - TUI: Command `export network json path/to/file.json`, inline warnings for suspicious entries.

### timeline_overview

- **Goal:** Produce a chronological timeline of key memory events.
- **Plugins:**
  1. `windows.timeliner`
  2. `windows.getservicesids`
- **Transforms:**
  - Normalize event timestamps, categorize event types.
- **Outputs:**
  - `timeline_events` table (timestamp, source, description, category).
- **UI Expectations:**
  - GUI: Timeline chart (future enhancement) and table view with filters.
  - TUI: Paginated table with search (`/time 2022-11-01`).

## Validation Rules

- Before executing, ensure selected workflow supports the memory image profile (Windows vs Linux vs macOS). For now focus on Windows; extend catalogue before claiming cross-platform support.
- Verify required symbol files or configuration options exist; if not, present actionable error.
- Provide dry-run mode that only validates prerequisites without executing plugins.

## Output Schema Mapping

- All workflows must map outputs to canonical schemas defined in `docs/schema/` (to be authored later).
- Schema names follow pattern `<workflow>_<artifact>.json`.
- Exporters rely on schema definitions to format CSV/Parquet columns consistently.

## Future Workflow Ideas (Backlog)

- `malware_hunt`: Incorporates YARA scanning and suspicious strings extraction.
- `memory_compare`: Diff two memory images to highlight process differences.
- `linux_quick_triage`: Equivalent to `quick_triage` but for Linux images (netscan variant, pslist.linux, etc.).

## Implementation Checklist

1. Create workflow definition data structures in `oroitz.core.workflow`.
2. Populate seed workflows matching the catalogue above.
3. Add unit tests ensuring plugin order, transforms, and output mapping align with spec.
4. Expose workflows to GUI/TUI through adapter endpoints (`list_workflows`, `describe_workflow`).
5. Document workflows in user docs with screenshots/terminal captures once UI exists.
