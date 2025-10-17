"""Workflow management for Oroitz."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from oroitz.core.telemetry import logger


class PluginSpec(BaseModel):
    """Specification for a Volatility plugin."""

    name: str = Field(..., min_length=1, description="Plugin name cannot be empty")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class TransformSpec(BaseModel):
    """Specification for output transformation."""

    name: str = Field(..., min_length=1, description="Transform name cannot be empty")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class WorkflowSpec(BaseModel):
    """Specification for a workflow."""

    id: str = Field(..., min_length=1, description="Workflow ID cannot be empty")
    name: str = Field(..., min_length=1, description="Workflow name cannot be empty")
    description: str = Field(..., min_length=1, description="Workflow description cannot be empty")
    plugins: List[PluginSpec] = Field(
        ..., min_length=1, description="Workflow must have at least one plugin"
    )
    transforms: List[TransformSpec] = Field(default_factory=list)
    supported_profiles: List[str] = Field(default_factory=list)  # e.g., ["windows"]


class WorkflowRegistry:
    """Registry for workflows."""

    def __init__(self) -> None:
        self._workflows: Dict[str, WorkflowSpec] = {}

    def register(self, workflow: WorkflowSpec) -> None:
        """Register a workflow."""
        if not isinstance(workflow, WorkflowSpec):
            raise TypeError("Workflow must be a WorkflowSpec instance")
        self._workflows[workflow.id] = workflow
        logger.info(f"Registered workflow: {workflow.id}")

    def get(self, workflow_id: str) -> Optional[WorkflowSpec]:
        """Get a workflow by ID."""
        if not isinstance(workflow_id, str) or not workflow_id:
            raise ValueError("Workflow ID must be a non-empty string")
        return self._workflows.get(workflow_id)

    def list(self) -> List[WorkflowSpec]:
        """List all registered workflows."""
        return list(self._workflows.values())

    def validate_compatibility(self, workflow_id: str, profile: str) -> bool:
        """Check if workflow is compatible with the given profile."""
        if not isinstance(workflow_id, str) or not workflow_id:
            raise ValueError("Workflow ID must be a non-empty string")
        if not isinstance(profile, str) or not profile:
            raise ValueError("Profile must be a non-empty string")

        workflow = self.get(workflow_id)
        if not workflow:
            return False
        return not workflow.supported_profiles or profile in workflow.supported_profiles

    def clear(self) -> None:
        """Clear all registered workflows."""
        self._workflows.clear()
        logger.info("Workflow registry cleared")


# Global registry instance
registry = WorkflowRegistry()


def seed_workflows() -> None:
    """Seed the registry with default workflows."""
    # quick_triage workflow
    quick_triage = WorkflowSpec(
        id="quick_triage",
        name="Quick Triage",
        description=(
            "Rapid overview of running processes, network connections, "
            "and suspicious memory regions"
        ),
        plugins=[
            PluginSpec(name="windows.pslist"),
            PluginSpec(name="windows.netscan"),
            PluginSpec(name="windows.malfind"),
        ],
        supported_profiles=[],  # Allow any profile for testing
    )
    registry.register(quick_triage)

    logger.info("Seeded default workflows")
