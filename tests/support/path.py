import sys
from pathlib import Path

_SERVER_ROOT = Path(__file__).resolve().parents[2] / "server"


def setup_server_import_path() -> None:
    server_path = str(_SERVER_ROOT)
    if server_path not in sys.path:
        sys.path.insert(0, server_path)
