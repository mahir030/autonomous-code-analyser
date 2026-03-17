from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
REPORT_FOLDER = BASE_DIR / "reports"

MAX_UPLOAD_SIZE_MB = 20
MAX_FILE_SIZE_MB = 2

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".java", ".cpp", ".c",
    ".cs", ".go", ".php", ".rb", ".ts"
}
