import os
import shutil
import uuid
import zipfile

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from backend.project_evaluator import evaluate_project
from backend.database import engine, Base
from backend.config import UPLOAD_FOLDER
from backend.reporting.pdf_generator import generate_pdf_report

app = FastAPI()
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("reports", exist_ok=True)


def extract_zip(zip_path: str) -> str:
    job_id = str(uuid.uuid4())
    extract_path = os.path.join(UPLOAD_FOLDER, job_id)
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    return extract_path


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload", response_class=HTMLResponse)
async def upload_project(request: Request, file: UploadFile = File(...)):

    zip_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extract_path = extract_zip(zip_path)

    overall_score, results, software_metrics = evaluate_project(zip_path, extract_path)

    report_id = str(uuid.uuid4())
    pdf_path = os.path.join("reports", f"{report_id}.pdf")

    generate_pdf_report(pdf_path, overall_score, software_metrics, results)

    shutil.rmtree(extract_path, ignore_errors=True)
    os.remove(zip_path)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "overall": overall_score,
            "results": results,
            "software_metrics": software_metrics,
            "pdf_path": pdf_path
        }
    )


@app.get("/download-report")
def download_report(path: str):
    return FileResponse(path, filename="SQA_Report.pdf", media_type="application/pdf")

