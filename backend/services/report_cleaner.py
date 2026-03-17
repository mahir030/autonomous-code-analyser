import time
from pathlib import Path


def delete_old_reports(report_dir, max_age_hours=24):

    report_dir = Path(report_dir).resolve()

    if not report_dir.exists() or not report_dir.is_dir():
        return

    now = time.time()
    max_age_seconds = max_age_hours * 3600

    for file in report_dir.glob("*.pdf"):

        try:
            if not file.is_file():
                continue

            age = now - file.stat().st_mtime

            if age > max_age_seconds:
                file.unlink(missing_ok=True)

        except Exception:
            continue
