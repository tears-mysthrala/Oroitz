import asyncio
import json
from pathlib import Path

from oroitz.core.executor import ExecutionResult
from oroitz.core.session import Session
from oroitz.core.workflow import registry, seed_workflows
from oroitz.ui.tui import OroitzTUI
from oroitz.ui.tui.views.results_view import ResultsView


async def main() -> None:
    # Load normalized quick_triage JSON
    results_path = Path("results_quick_triage_memdump.json")
    data = json.loads(results_path.read_text(encoding="utf-8"))

    users = data.get("users", [])
    if not users:
        print("No users found in normalized results")
        return

    # Convert normalized users back to raw-like dicts expected from windows.getsids
    raw_users = []
    for u in users:
        raw_users.append(
            {
                "Name": u.get("name"),
                "SID": u.get("sid"),
                "PID": u.get("pid"),
                "Process": u.get("process"),
            }
        )

    # Build ExecutionResult list with only getsids
    exec_results = [
        ExecutionResult(
            plugin_name="windows.getsids",
            success=True,
            output=raw_users,
            error=None,
            duration=0.0,
            timestamp=0.0,
        )
    ]

    # Prepare session & workflow
    seed_workflows()
    workflow = registry.get("quick_triage")
    assert workflow is not None
    session = Session(image_path=Path("samples/memdump.mem"))

    # Use Textual test harness to mount the ResultsView and inspect the users table
    app = OroitzTUI()
    async with app.run_test() as pilot:
        app.push_screen(ResultsView(workflow, session, exec_results))
        # Poll for the users table to appear
        users_table = None
        for _ in range(20):
            await pilot.pause()
            try:
                users_table = app.query_one("#users-table")
                break
            except Exception:
                continue
        if users_table is None:
            print("Users table not found")
            return
        # DataTable has row_count attribute in recent Textual; fallback to internal method
        row_count = getattr(users_table, "row_count", None)
        if row_count is None:
            # Fallback: try to access underlying table data
            row_count = len(getattr(users_table, "rows", []))

        print(f"TUI Users rows: {row_count}")


if __name__ == "__main__":
    asyncio.run(main())
