"""Session management for Oroitz."""

from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from oroitz.core.executor import ExecutionResult
from oroitz.core.output import QuickTriageOutput


class Session(BaseModel):
    """Represents an analysis session."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(default="Untitled Session")
    image_path: Optional[Path] = None
    workflow_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def save(self, path: Path) -> None:
        """Save session to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, path: Path) -> "Session":
        """Load session from file."""
        with open(path, "r") as f:
            data = f.read()
        return cls.model_validate_json(data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup if needed
        pass

    def run(
        self, workflow_id: str, options: Optional[dict] = None
    ) -> Optional["QuickTriageOutput"]:
        """Run a workflow and return normalized results."""

        from oroitz.core.cache import Cache
        from oroitz.core.executor import Executor
        from oroitz.core.output import OutputNormalizer
        from oroitz.core.workflow import registry

        workflow = registry.get(workflow_id)
        if not workflow:
            return None

        if not self.image_path:
            return None

        # Check compatibility - Volatility 3 auto-detects OS, so we validate plugin OS prefix
        if not registry.validate_compatibility(workflow_id):
            return None

        executor = Executor()
        normalizer = OutputNormalizer()
        cache = Cache()  # Uses default cache dir

        results = []
        for plugin_spec in workflow.plugins:
            # Check cache first
            cached = cache.get(self.id, plugin_spec.name, plugin_spec.parameters)
            if cached is not None:
                result = ExecutionResult(
                    plugin_name=plugin_spec.name,
                    success=True,
                    output=cached,
                    error=None,
                    duration=0.0,
                    timestamp=0.0,  # Not cached
                )
            else:
                result = executor.execute_plugin(
                    plugin_spec.name,
                    str(self.image_path),
                    session_id=self.id,
                    **plugin_spec.parameters,
                )
                if result.success:
                    cache.set(self.id, plugin_spec.name, plugin_spec.parameters, result.output)

            results.append(result)

        # For now, assume quick_triage
        if workflow_id == "quick_triage":
            return normalizer.normalize_quick_triage(results)
        else:
            # For other workflows, return None or implement later
            return None


class SessionManager:
    """Manages analysis sessions."""

    def __init__(self, sessions_dir: Optional[Path] = None) -> None:
        """Initialize session manager."""
        self.sessions_dir = sessions_dir or Path.home() / ".oroitz" / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._sessions: dict[str, Session] = {}
        self._load_sessions()

    def _load_sessions(self) -> None:
        """Load existing sessions from disk."""
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                session = Session.load(session_file)
                self._sessions[session.id] = session
            except Exception:
                # Skip corrupted session files
                continue

    def create_session(
        self,
        name: str = "Untitled Session",
        image_path: Optional[Path] = None,
        workflow_id: Optional[str] = None,
    ) -> Session:
        """Create a new session."""
        session = Session(name=name, image_path=image_path, workflow_id=workflow_id)
        self._sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[Session]:
        """List all sessions, sorted by creation date (newest first)."""
        return sorted(self._sessions.values(), key=lambda s: s.created_at, reverse=True)

    def save_sessions(self) -> None:
        """Save all sessions to disk."""
        for session in self._sessions.values():
            session_path = self.sessions_dir / f"{session.id}.json"
            session.save(session_path)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            session_path = self.sessions_dir / f"{session_id}.json"
            if session_path.exists():
                session_path.unlink()
            del self._sessions[session_id]
            return True
        return False
