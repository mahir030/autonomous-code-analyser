import os

SUPPORTED_EXTENSIONS = [
    ".py", ".js", ".java", ".cpp", ".c", ".cs",
    ".go", ".php", ".rb", ".ts"
]

def scan_project(path: str):
    files = []

    for root, _, filenames in os.walk(path):
        for file in filenames:
            if any(file.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                full_path = os.path.join(root, file)
                files.append(full_path)

    return files

