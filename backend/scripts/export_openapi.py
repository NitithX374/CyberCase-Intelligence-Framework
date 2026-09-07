import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app

schema = app.app.openapi()
Path(sys.argv[1]).write_text(json.dumps(schema, ensure_ascii=False), encoding="utf-8")
