"""Forwarding test runner for AttacKG+ test suite from backend directory."""

from pathlib import Path
import sys

WORKSPACE_DIR = Path(__file__).resolve().parents[2]
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from experiments.attackg_plus.tests.test_attackg_plus import *  # noqa: F401, F403
