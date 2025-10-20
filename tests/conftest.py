"""
Pytest configuration for Oroitz tests.
Ensures Textual is imported before PySide6 to avoid import conflicts.
"""

import os

# Set environment variables to minimize PySide6 interference
os.environ["SHIBOKEN_DISABLE_SIGNATURE_CACHE"] = "1"
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/dev/null"

# Import textual FIRST, before any PySide6 code
import textual  # noqa: F401
from textual.widgets import Button, DataTable, Input, Select  # noqa: F401