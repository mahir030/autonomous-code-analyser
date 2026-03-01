import os
from backend.services.file_scanner import scan_project

from backend.metrics.efficiency import calculate_efficiency
from backend.metrics.optimization import calculate_optimization
from backend.metrics.maintainability import calculate_maintainability
from backend.metrics.reliability import calculate_reliability
from backend.metrics.security import calculate_security
from backend.metrics.portability import calculate_portability


def detect_language(filename):
    ext = filename.split(".")[-1].lower()

    mapping = {
        "py": "Python",
        "js": "JavaScript",
        "java": "Java",
        "c": "C",
        "cpp": "C++",
        "cs": "C#",
        "php": "PHP",
        "go": "Go",
        "rb": "Ruby",
        "ts": "TypeScript"
    }

    return mapping.get(ext, "Unknown")


def count_lines(file_path):
    try:
        with open(file_path, "r", errors="ignore") as f:
            return len(f.readlines())
    except:
        return 0


def read_code(file_path):
    try:
        with open(file_path, "r", errors="ignore") as f:
            return f.read()
    except:
        return ""


def evaluate_project(zip_path, extract_path):

    files = scan_project(extract_path)
    file_results = []

    for file in files:

        loc = count_lines(file)
        code = read_code(file)
        language = detect_language(file)

               # metrics
        efficiency = calculate_efficiency(loc)
        optimization = calculate_optimization(loc / 100)
        maintainability = calculate_maintainability(loc)

        # pass code to analyzers
        reliability = calculate_reliability(code, language)

        security_data = calculate_security(code)
        security = security_data["score"]
        security_issues = security_data["issues"]

        portability = calculate_portability()

        score = (
            efficiency +
            optimization +
            maintainability +
            reliability +
            security +
            portability
        ) / 6

        breakdown = {
            "efficiency": round(efficiency * 100, 2),
            "optimization": round(optimization * 100, 2),
            "maintainability": round(maintainability * 100, 2),
            "reliability": round(reliability * 100, 2),
            "security": round(security * 100, 2),
            "portability": round(portability * 100, 2)
        }

        file_results.append({
            "filename": os.path.basename(file),
            "language": language,
            "loc": loc,
            "score": round(score * 100, 2),
            "breakdown": breakdown,
            "security_issues": security_issues
        })

    overall_score = round(
        sum(file["score"] for file in file_results) / len(file_results), 2
    ) if file_results else 0

    software_metrics = {
        "efficiency": round(sum(f["breakdown"]["efficiency"] for f in file_results) / len(file_results), 2) if file_results else 0,
        "optimization": round(sum(f["breakdown"]["optimization"] for f in file_results) / len(file_results), 2) if file_results else 0,
        "maintainability": round(sum(f["breakdown"]["maintainability"] for f in file_results) / len(file_results), 2) if file_results else 0,
        "reliability": round(sum(f["breakdown"]["reliability"] for f in file_results) / len(file_results), 2) if file_results else 0,
        "security": round(sum(f["breakdown"]["security"] for f in file_results) / len(file_results), 2) if file_results else 0,
        "portability": round(sum(f["breakdown"]["portability"] for f in file_results) / len(file_results), 2) if file_results else 0,
    }

    return overall_score, file_results, software_metrics
