import shutil
from pathlib import Path


class CleanupManager:

    SAFE_ROOTS = {"uploads", "reports"}

    @staticmethod
    def _is_safe_path(path: Path):
        resolved = path.resolve()
        return any(part in CleanupManager.SAFE_ROOTS for part in resolved.parts)

    @staticmethod
    def remove_file(path):
        path = Path(path).resolve()
        if path.exists() and path.is_file() and CleanupManager._is_safe_path(path):
            path.unlink(missing_ok=True)

    @staticmethod
    def remove_directory(path):
        path = Path(path).resolve()
        if path.exists() and path.is_dir() and CleanupManager._is_safe_path(path):
            shutil.rmtree(path, ignore_errors=True)

    @staticmethod
    def clear_pycache(root):
        root = Path(root).resolve()
        for pycache in root.rglob("__pycache__"):
            if CleanupManager._is_safe_path(pycache):
                shutil.rmtree(pycache, ignore_errors=True)
