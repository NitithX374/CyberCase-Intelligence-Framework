import subprocess
import sys
from pathlib import Path

from app.routers import documentIngestion as router
from app.services.document_ingestion.recognition.typhoon import TyphoonDocumentRecognizer


def test_typhoon_router_loads_without_optional_google_packages(monkeypatch):
    monkeypatch.setenv("DOCUMENT_RECOGNIZER", "typhoon")
    script = """
import importlib.abc
import sys

class NoGooglePackages(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "google" or fullname.startswith("google."):
            raise ModuleNotFoundError("Google packages intentionally unavailable")

sys.meta_path.insert(0, NoGooglePackages())
from app.routers.documentIngestion import _build_recognizer
from app.services.document_ingestion.recognition.typhoon import TyphoonDocumentRecognizer
assert isinstance(_build_recognizer(), TyphoonDocumentRecognizer)
"""
    backend_root = str(Path(__file__).resolve().parent.parent)
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=backend_root,
    )
    assert result.returncode == 0, result.stderr


def test_recognizer_is_typhoon():
    recognizer = router._build_recognizer()
    assert isinstance(recognizer, TyphoonDocumentRecognizer)
