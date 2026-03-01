import os
from pathlib import Path
from backend.config import MAX_FILE_SIZE_MB, SUPPORTED_EXTENSIONS


def scan_project(path):
    base_path = Path(path).resolve()
    files = []
    max_size = MAX_FILE_SIZE_MB * 1024 * 1024

    for root, dirs, filenames in os.walk(base_path):

        dirs[:] = [
            d for d in dirs
            if not d.startswith(".")
            and d not in {"__pycache__", "venv", "env", ".git"}
        ]

        for filename in filenames:

            file_path = (Path(root) / filename).resolve()

            if not file_path.suffix in SUPPORTED_EXTENSIONS:
                continue

            if not str(file_path).startswith(str(base_path)):
                continue

            if file_path.is_symlink():
                continue

            try:
                if file_path.stat().st_size <= max_size:
                    files.append(str(file_path))
            except Exception:
                continue

    return files
