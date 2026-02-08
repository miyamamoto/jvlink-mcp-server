"""Live tests require keiba.db — skip in CI."""
import os, pytest

def pytest_collection_modifyitems(config, items):
    db_path = os.environ.get("DB_PATH", "/tmp/keiba.db")
    if not os.path.exists(db_path):
        skip = pytest.mark.skip(reason=f"keiba.db not found at {db_path}")
        for item in items:
            item.add_marker(skip)
