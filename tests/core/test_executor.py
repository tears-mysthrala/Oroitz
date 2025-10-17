"""Tests for executor module."""

from oroitz.core.executor import Executor


def test_executor_creation():
    """Test executor creation."""
    executor = Executor()
    assert executor.max_concurrency == 4  # from config


def test_execute_plugin_mock():
    """Test executing mock plugins."""
    executor = Executor()

    # Test pslist
    result = executor.execute_plugin("windows.pslist", "/fake/image", "windows")
    assert result.plugin_name == "windows.pslist"
    assert result.success
    assert result.output is not None
    assert len(result.output) == 2  # mock data
    assert result.duration >= 0

    # Test netscan
    result = executor.execute_plugin("windows.netscan", "/fake/image", "windows")
    assert result.plugin_name == "windows.netscan"
    assert result.success
    assert result.output is not None
    assert len(result.output) == 1

    # Test malfind
    result = executor.execute_plugin("windows.malfind", "/fake/image", "windows")
    assert result.plugin_name == "windows.malfind"
    assert result.success
    assert result.output is not None
    assert len(result.output) == 1


def test_execute_unknown_plugin():
    """Test executing unknown plugin."""
    executor = Executor()

    result = executor.execute_plugin("unknown.plugin", "/fake/image", "windows")
    assert result.plugin_name == "unknown.plugin"
    assert result.success
    assert result.output == []


def test_execute_workflow():
    """Test executing a complete workflow."""
    from oroitz.core.workflow import PluginSpec, WorkflowSpec

    executor = Executor()

    workflow = WorkflowSpec(
        id="test",
        name="Test",
        description="Test workflow",
        plugins=[
            PluginSpec(name="windows.pslist"),
            PluginSpec(name="windows.netscan"),
        ],
    )

    results = executor.execute_workflow(workflow, "/fake/image", "windows")

    assert len(results) == 2
    assert all(r.success for r in results)
    assert results[0].plugin_name == "windows.pslist"
    assert results[1].plugin_name == "windows.netscan"
