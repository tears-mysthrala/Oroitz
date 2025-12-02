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

    def validate_compatibility(self, workflow_id: str) -> bool:
        """Check if workflow is compatible (Volatility 3 auto-detects OS from plugins)."""
        if not isinstance(workflow_id, str) or not workflow_id:
            raise ValueError("Workflow ID must be a non-empty string")

        workflow = self.get(workflow_id)
        if not workflow:
            return False
        # In Volatility 3, compatibility is determined by plugin OS prefixes
        # (windows.*, linux.*, mac.*). We assume workflows are correctly defined
        return True

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
            PluginSpec(name="windows.getsids"),
        ],
    )
    registry.register(quick_triage)

    # process_deepdive workflow
    process_deepdive = WorkflowSpec(
        id="process_deepdive",
        name="Process Deep Dive",
        description=("Exhaustive process tree analysis including DLL listings and handles"),
        plugins=[
            PluginSpec(name="windows.pstree"),
            PluginSpec(name="windows.dlllist"),
            PluginSpec(name="windows.handles"),
            PluginSpec(name="windows.psscan"),
        ],
    )
    registry.register(process_deepdive)

    # network_focus workflow
    network_focus = WorkflowSpec(
        id="network_focus",
        name="Network Focus",
        description=("Highlight network activity, sockets, and associated processes"),
        plugins=[
            PluginSpec(name="windows.netscan"),
        ],
    )
    registry.register(network_focus)

    # full_system_scan workflow
    full_system_scan = WorkflowSpec(
        id="full_system_scan",
        name="Full System Scan",
        description=(
            "Complete analysis including all available plugins for comprehensive forensics"
        ),
        plugins=[
            PluginSpec(name="windows.pslist"),
            PluginSpec(name="windows.netscan"),
            PluginSpec(name="windows.malfind"),
            PluginSpec(name="windows.pstree"),
            PluginSpec(name="windows.dlllist"),
            PluginSpec(name="windows.handles"),
            PluginSpec(name="windows.psscan"),
            PluginSpec(name="timeliner.Timeliner"),
            PluginSpec(name="windows.getservicesids"),
        ],
    )
    registry.register(full_system_scan)

    # malware_hunt workflow
    malware_hunt = WorkflowSpec(
        id="malware_hunt",
        name="Malware Hunt",
        description=(
            "Focused scan for malware indicators, suspicious processes, and injected code"
        ),
        plugins=[
            PluginSpec(name="windows.malfind"),
            PluginSpec(name="windows.psscan"),
            PluginSpec(name="windows.dlllist"),
            PluginSpec(name="windows.handles"),
            PluginSpec(name="windows.modscan"),
        ],
    )
    registry.register(malware_hunt)

    # memory_analysis workflow
    memory_analysis = WorkflowSpec(
        id="memory_analysis",
        name="Memory Analysis",
        description=("Detailed memory structure analysis including pools, heaps, and allocations"),
        plugins=[
            PluginSpec(name="windows.poolscanner"),
            PluginSpec(name="windows.bigpoolscan"),
            PluginSpec(name="windows.memmap"),
        ],
    )
    registry.register(memory_analysis)

    # timeline_overview workflow
    timeline_overview = WorkflowSpec(
        id="timeline_overview",
        name="Timeline Overview",
        description=("Chronological view of system events and process activities"),
        plugins=[
            PluginSpec(name="timeliner.Timeliner"),
            PluginSpec(name="windows.pslist"),
        ],
    )
    registry.register(timeline_overview)

    logger.info("Seeded default workflows")

    # account_enumeration workflow (attempts to derive users/hashes from memory)
    account_enumeration = WorkflowSpec(
        id="account_enumeration",
        name="Account Enumeration",
        description=(
            "Enumerate user SIDs and attempt hash extraction from memory (SAM/LSA if available)"
        ),
        plugins=[
            PluginSpec(name="windows.getsids"),
            PluginSpec(name="windows.hashdump"),
            PluginSpec(name="windows.cachedump"),
        ],
    )
    registry.register(account_enumeration)
