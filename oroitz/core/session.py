"""Session management for Oroitz."""

from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class Session(BaseModel):
    """Represents an analysis session."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(default="Untitled Session")
    image_path: Optional[Path] = None
    profile: Optional[str] = None
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