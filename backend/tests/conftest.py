"""Pytest configuration — adds the backend root to sys.path."""
import sys
from pathlib import Path

# Ensure ``app`` package is importable when running pytest from any directory.
sys.path.insert(0, str(Path(__file__).parent.parent))
