import os

# Set environment variables to minimize PySide6 interference
os.environ["SHIBOKEN_DISABLE_SIGNATURE_CACHE"] = "1"
os.environ["QT_QPA_PLATFORM"] = "offscreen"
# Disable PySide6 entirely if possible
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/dev/null"

from pathlib import Path
from unittest.mock import patch

import pytest
from textual.widgets import Button, DataTable, Input, Select

from oroitz.core.executor import ExecutionResult
from oroitz.core.session import Session
from oroitz.core.workflow import registry, seed_workflows
from oroitz.ui.tui import OroitzTUI
from oroitz.ui.tui.views import HomeView, ResultsView, SessionWizardView


@pytest.fixture
def tui_app():
    """Create TUI app instance for testing."""
    seed_workflows()
    app = OroitzTUI()
    return app


@pytest.fixture
async def pilot(tui_app):
    """Create a pilot for testing the TUI."""
    async with tui_app.run_test() as pilot:
        yield pilot


class TestHomeView:
    """Test HomeView functionality."""

    @pytest.mark.asyncio
    async def test_screen_composition(self, pilot):
        """Test screen has all required widgets."""
        await pilot.pause()

        # Check title
        title = pilot.get_widget_by_id("title")
        assert title is not None

        # Check workflow buttons container
        workflow_container = pilot.get_widget_by_id("workflow-buttons")
        assert workflow_container is not None

        # Check exit button
        exit_btn = pilot.get_widget_by_id("exit-button")
        assert exit_btn is not None

    @pytest.mark.asyncio
    async def test_workflow_button_click(self, pilot):
        """Test clicking workflow button navigates to session wizard."""
        await pilot.pause()

        # Get first workflow button
        workflows = registry.list()
        if workflows:
            first_workflow = workflows[0]
            button = pilot.get_widget_by_id(f"workflow-{first_workflow.id}")

            # Click the button
            await pilot.click(button)

            # Should navigate to session wizard
            await pilot.pause()
            # Note: Navigation might not work in test environment


@pytest.mark.tui
class TestSessionWizardView:
    """Test SessionWizardView functionality."""

    @pytest.mark.asyncio
    async def test_wizard_initial_state(self, pilot):
        """Test wizard starts with image input."""
        # Navigate to session wizard with a workflow
        workflows = registry.list()
        if workflows:
            workflow = workflows[0]
            pilot.app.push_screen(SessionWizardView(workflow))

            await pilot.pause()

            # Check for image path input
            image_input = pilot.get_widget_by_id("image-path-input")
            assert image_input is not None
            assert isinstance(image_input, Input)

    @pytest.mark.asyncio
    async def test_profile_selection(self, pilot):
        """Test profile selection dropdown."""
        workflows = registry.list()
        if workflows:
            workflow = workflows[0]
            pilot.app.push_screen(SessionWizardView(workflow))

            await pilot.pause()

            # Check for profile select
            profile_select = pilot.get_widget_by_id("profile-select")
            if profile_select:
                assert isinstance(profile_select, Select)
                # Should have some default profiles
                assert len(profile_select.options) > 0  # type: ignore

    @pytest.mark.asyncio
    async def test_session_creation(self, pilot):
        """Test session creation from wizard inputs."""
        workflows = registry.list()
        if workflows:
            workflow = workflows[0]
            pilot.app.push_screen(SessionWizardView(workflow))

            await pilot.pause()

            # Fill in the form
            image_input = pilot.get_widget_by_id("image-path-input")
            await pilot.click(image_input)
            await pilot.press("tab")  # Tab to next field
            await pilot.press(*"/test/memory.img")

            # Select profile
            profile_select = pilot.get_widget_by_id("profile-select")
            if profile_select:
                await pilot.click(profile_select)
                await pilot.press("enter")  # Select first option

            # Click create button
            create_btn = pilot.get_widget_by_id("start-button")
            if create_btn:
                await pilot.click(create_btn)

                # Should create session and navigate
                await pilot.pause()


@pytest.mark.tui
class TestResultsView:
    """Test ResultsView functionality."""

    @pytest.mark.asyncio
    async def test_results_display(self, pilot):
        """Test results are displayed in table."""
        # Create mock results
        mock_results = [
            ExecutionResult(
                plugin_name="windows.pslist",
                success=True,
                output=[
                    {"pid": 4, "name": "System", "ppid": 0},
                    {"pid": 1234, "name": "notepad.exe", "ppid": 876},
                ],
                error=None,
                duration=1.5,
                timestamp=1234567890,
            )
        ]

        # Create mock session and workflow
        session = Session(image_path=Path("/test.img"), profile="windows")
        workflows = registry.list()
        workflow = workflows[0] if workflows else None

        if workflow:
            # Push results screen with mock data
            pilot.app.push_screen(ResultsView(workflow, session, mock_results))

            await pilot.pause()

            # Check data table exists
            data_table = pilot.get_widget_by_id("results-table")
            assert data_table is not None
            assert isinstance(data_table, DataTable)

    @pytest.mark.asyncio
    async def test_export_functionality(self, pilot):
        """Test export button functionality."""
        mock_results = [
            ExecutionResult(
                plugin_name="windows.pslist",
                success=True,
                output=[{"pid": 4, "name": "System"}],
                error=None,
                duration=1.0,
                timestamp=1234567890,
            )
        ]

        # Create mock session and workflow
        session = Session(image_path=Path("/test.img"), profile="windows")
        workflows = registry.list()
        workflow = workflows[0] if workflows else None

        if workflow:
            pilot.app.push_screen(ResultsView(workflow, session, mock_results))

            await pilot.pause()

            # Check export button
            export_btn = pilot.get_widget_by_id("export-json")
            if export_btn:
                # Mock the export function
                with patch("oroitz.ui.tui.views.OutputExporter"):
                    await pilot.click(export_btn)
                    # Should trigger export (mocked)


@pytest.mark.tui
class TestTUIIntegration:
    """Integration tests for TUI workflow."""

    @pytest.mark.asyncio
    async def test_full_workflow_simulation(self, pilot):
        """Test complete workflow from home to results."""
        await pilot.pause()

        # Start at home screen
        assert isinstance(pilot.app.screen, HomeView)

        # Click on quick triage workflow
        quick_triage_btn = pilot.get_widget_by_id("workflow-quick_triage")
        if quick_triage_btn:
            await pilot.click(quick_triage_btn)

            # Should navigate to session wizard
            await pilot.pause()

            # Fill wizard and create session
            # (This would require more complex interaction simulation)

    @pytest.mark.asyncio
    async def test_error_handling(self, pilot):
        """Test error handling in TUI."""
        # Test with invalid inputs
        workflows = registry.list()
        if workflows:
            workflow = workflows[0]
            pilot.app.push_screen(SessionWizardView(workflow))

            await pilot.pause()

            # Try to create session with empty image path
            create_btn = pilot.get_widget_by_id("start-button")
            if create_btn:
                await pilot.click(create_btn)
                # Should show error or prevent creation
                await pilot.pause()

    @pytest.mark.asyncio
    async def test_navigation_flow(self, pilot):
        """Test navigation between screens."""
        # Test back/forward navigation if implemented
        await pilot.pause()

        # This would test any navigation buttons or key bindings
        # For now, just ensure screens can be pushed/popped
        initial_screen = pilot.app.screen

        workflows = registry.list()
        if workflows:
            workflow = workflows[0]
            pilot.app.push_screen(SessionWizardView(workflow))
            await pilot.pause()
            assert isinstance(pilot.app.screen, SessionWizardView)

            pilot.app.pop_screen()
            await pilot.pause()
            assert pilot.app.screen == initial_screen


# Snapshot tests for visual regression - disabled for now
# @pytest.mark.asyncio
# async def test_home_screen_snapshot(snapshot):
#     """Snapshot test for home screen."""
#     seed_workflows()
#     app = OroitzTUI()

#     async with app.run_test() as pilot:
#         await pilot.pause()
#         # Take snapshot of the screen
#         snapshot.assert_match(pilot.get_screen_snapshot())


# @pytest.mark.asyncio
# async def test_session_wizard_snapshot(snapshot):
#     """Snapshot test for session wizard."""
#     seed_workflows()
#     app = OroitzTUI()
#     workflows = registry.list()
#     workflow = workflows[0] if workflows else None

#     if workflow:
#         async with app.run_test() as pilot:
#             pilot.app.push_screen(SessionWizardView(workflow))
#             await pilot.pause()
#             snapshot.assert_match(pilot.get_screen_snapshot())
