import zipfile
import os
import shutil
import uuid

def save_and_extract(zip_file, upload_dir):
    job_id = str(uuid.uuid4())
    extract_path = os.path.join(upload_dir, job_id)

    os.makedirs(extract_path, exist_ok=True)

    zip_path = os.path.join(extract_path, "project.zip")

    with open(zip_path, "wb") as f:
        f.write(zip_file)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    os.remove(zip_path)

    return extract_path

