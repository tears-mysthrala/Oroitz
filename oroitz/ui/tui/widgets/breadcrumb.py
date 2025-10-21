"""Breadcrumb widget for TUI navigation."""

from textual.widgets import Static


class Breadcrumb(Static):
    """Breadcrumb widget showing current navigation path."""

    def __init__(self, path: str = "", **kwargs):
        super().__init__(f"📍 {path}", **kwargs)
        self.path = path

    def update_path(self, path: str) -> None:
        """Update the breadcrumb path."""
        self.path = path
        self.update(f"📍 {path}")
