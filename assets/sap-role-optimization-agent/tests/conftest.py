"""Configure sys.path for the custom tests/ directory.

Uses pytest_configure hook to ensure app/ is on sys.path before
collection begins, so peer-level imports resolve at import time.
"""
import sys
from pathlib import Path


def pytest_configure(config):
    """Add app/ to sys.path before test collection so peer imports resolve."""
    _app_path = str(Path(__file__).parent.parent / "app")
    if _app_path not in sys.path:
        sys.path.insert(0, _app_path)
