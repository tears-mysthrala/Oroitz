"""Tests for workflow module."""

from oroitz.core.workflow import WorkflowSpec, PluginSpec, registry, seed_workflows


def test_workflow_spec_creation():
    """Test creating a workflow specification."""
    workflow = WorkflowSpec(
        id="test_workflow",
        name="Test Workflow",
        description="A test workflow",
        plugins=[
            PluginSpec(name="test.plugin1"),
            PluginSpec(name="test.plugin2", parameters={"param1": "value1"}),
        ],
        supported_profiles=["windows", "linux"],
    )

    assert workflow.id == "test_workflow"
    assert workflow.name == "Test Workflow"
    assert len(workflow.plugins) == 2
    assert workflow.supported_profiles == ["windows", "linux"]


def test_workflow_registry():
    """Test workflow registry operations."""
    # Clear registry
    registry.clear()

    # Register a workflow
    workflow = WorkflowSpec(
        id="test",
        name="Test",
        description="Test workflow",
        plugins=[PluginSpec(name="test.plugin")],
    )
    registry.register(workflow)

    # Get workflow
    retrieved = registry.get("test")
    assert retrieved is not None
    assert retrieved.id == "test"

    # List workflows
    workflows = registry.list()
    assert len(workflows) == 1
    assert workflows[0].id == "test"

    # Test non-existent workflow
    assert registry.get("nonexistent") is None


def test_workflow_compatibility():
    """Test workflow compatibility validation."""
    # Clear registry
    registry.clear()

    # Register workflow with specific profiles
    workflow = WorkflowSpec(
        id="windows_only",
        name="Windows Only",
        description="Windows workflow",
        plugins=[PluginSpec(name="windows.test")],
        supported_profiles=["windows"],
    )
    registry.register(workflow)

    # Test compatibility
    assert registry.validate_compatibility("windows_only", "windows")
    assert not registry.validate_compatibility("windows_only", "linux")
    assert not registry.validate_compatibility("nonexistent", "windows")


def test_seed_workflows():
    """Test seeding default workflows."""
    # Clear registry
    registry.clear()

    # Seed workflows
    seed_workflows()

    # Check quick_triage exists
    workflow = registry.get("quick_triage")
    assert workflow is not None
    assert workflow.name == "Quick Triage"
    assert len(workflow.plugins) == 3
    assert workflow.supported_profiles == []