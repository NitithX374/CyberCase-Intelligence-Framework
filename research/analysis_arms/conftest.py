import importlib.util
import os
import sys
from pathlib import Path

BACKEND = os.environ.get("CYBERCASE_ARMS_BACKEND")

if BACKEND:
    backend = Path(BACKEND).resolve()
    sys.path[:0] = [str(backend), str(backend / "tests")]
    spec = importlib.util.spec_from_file_location(
        "pinned_backend_conftest", backend / "tests" / "conftest.py"
    )
    pinned = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pinned)
    globals().update({name: value for name, value in vars(pinned).items() if name[0] != "_"})
else:
    collect_ignore = ["tests"]
