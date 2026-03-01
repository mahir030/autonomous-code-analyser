import os
import shutil
import uuid
import zipfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from backend.project_evaluator import evaluate_project
from backend.reporting.pdf_generator import generate_pdf_report
from backend.services.report_cleaner import delete_old_reports
from backend.config import (
    UPLOAD_FOLDER,
    REPORT_FOLDER,
    MAX_UPLOAD_SIZE_MB,
)
from backend.utils.cleanup import CleanupManager


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER.mkdir(exist_ok=True)
REPORT_FOLDER.mkdir(exist_ok=True)


@app.on_event("startup")
async def startup_tasks():
    delete_old_reports(REPORT_FOLDER, 24)


# -----------------------------
# Secure ZIP Extraction
# -----------------------------
def secure_extract_zip(zip_path: Path, extract_to: Path):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for member in zip_ref.infolist():

            member_path = (extract_to / member.filename).resolve()

            # Zip Slip Protection
            if not str(member_path).startswith(str(extract_to.resolve())):
                raise HTTPException(status_code=400, detail="Invalid ZIP structure detected")

            zip_ref.extract(member, extract_to)


# -----------------------------
# Routes
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload", response_class=HTMLResponse)
async def upload_project(request: Request, file: UploadFile = File(...)):

    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files allowed")

    contents = await file.read()
    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if len(contents) > max_bytes:
        raise HTTPException(status_code=413, detail="File too large")

    job_id = uuid.uuid4().hex
    zip_path = UPLOAD_FOLDER / f"{job_id}.zip"

    with open(zip_path, "wb") as f:
        f.write(contents)

    extract_path = UPLOAD_FOLDER / job_id
    extract_path.mkdir(exist_ok=True)

    secure_extract_zip(zip_path, extract_path)

    overall, results, software_metrics = evaluate_project(zip_path, extract_path)

    report_id = uuid.uuid4().hex
    pdf_path = REPORT_FOLDER / f"{report_id}.pdf"

    generate_pdf_report(str(pdf_path), overall, software_metrics, results)

    # Cleanup uploaded data immediately after evaluation
    CleanupManager.remove_file(zip_path)
    CleanupManager.remove_directory(extract_path)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "overall": overall,
            "results": results,
            "software_metrics": software_metrics,
            "report_id": report_id
        }
    )


@app.get("/download-report/{report_id}")
def download_report(report_id: str):

    safe_path = (REPORT_FOLDER / f"{report_id}.pdf").resolve()

    if not str(safe_path).startswith(str(REPORT_FOLDER.resolve())):
        raise HTTPException(status_code=403)

    if not safe_path.exists():
        raise HTTPException(status_code=404)

    return FileResponse(str(safe_path), filename="SQA_Report.pdf")
