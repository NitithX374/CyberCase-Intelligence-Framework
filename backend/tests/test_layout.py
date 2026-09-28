from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app"


def test_no_test_sits_beside_the_code():
    beside = sorted(
        path.relative_to(APP).as_posix()
        for pattern in ("test_*.py", "*_test.py", "conftest.py")
        for path in APP.rglob(pattern)
    )
    assert beside == [], "backend tests live in backend/tests/"
