import os
from backend.services.file_scanner import scan_project
from backend.metrics.efficiency import calculate_efficiency
from backend.metrics.optimization import calculate_optimization
from backend.metrics.maintainability import calculate_maintainability
from backend.metrics.reliability import calculate_reliability
from backend.metrics.security import calculate_security
from backend.metrics.portability import calculate_portability
from backend.utils.cleanup import CleanupManager


# --------------------------------------------------
# Python Validation
# --------------------------------------------------

def is_python_file(file_path):
    return file_path.lower().endswith(".py")


# --------------------------------------------------
# File Helpers
# --------------------------------------------------

def count_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for line in f if line.strip())
    except Exception:
        return 0


def read_code(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def read_dependencies(extract_path):
    """
    Python dependency scanning using requirements.txt
    """
    requirements_path = os.path.join(extract_path, "requirements.txt")

    if os.path.exists(requirements_path):
        try:
            with open(requirements_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return None

    return None


# --------------------------------------------------
# MAIN PROJECT EVALUATION (PYTHON ONLY)
# --------------------------------------------------

def evaluate_project(zip_path, extract_path):
    file_results = []

    try:
        all_files = scan_project(extract_path)
        python_files = [f for f in all_files if is_python_file(f)]
        dependencies = read_dependencies(extract_path)

        if not python_files:
            return 0, [], {
                "Files Analyzed": 0,
                "Average Score": 0,
                "Note": "No Python files found in project."
            }

        for file in python_files:
            loc = count_lines(file)
            code = read_code(file)

            if not code.strip():
                continue

            # -------------------------
            # Python-Centric Metrics
            # -------------------------

            efficiency_score = calculate_efficiency(code, loc)

            optimization_data = calculate_optimization(code)
            optimization_score = optimization_data.get("score", 0)

            maintainability_score = calculate_maintainability(code, loc)

            # Reliability now explicitly Python
            reliability_score = calculate_reliability(code, language="python")

            # Security includes dependency check
            security_data = calculate_security(code, dependencies)
            security_score = security_data.get("score", 0)

            portability_score = calculate_portability(code, language="python")

            # -------------------------
            # Weighted Breakdown (More Realistic)
            # -------------------------

            weights = {
                "Efficiency": 0.20,
                "Optimization": 0.15,
                "Maintainability": 0.20,
                "Reliability": 0.20,
                "Security": 0.20,
                "Portability": 0.05,
            }

            breakdown_raw = {
                "Efficiency": efficiency_score,
                "Optimization": optimization_score,
                "Maintainability": maintainability_score,
                "Reliability": reliability_score,
                "Security": security_score,
                "Portability": portability_score,
            }

            breakdown = {
                key: round(value * 100, 2)
                for key, value in breakdown_raw.items()
            }

            # Weighted final score
            final_score = round(
                sum(breakdown_raw[k] * weights[k] for k in weights) * 100,
                2
            )

            file_results.append({
                "filename": os.path.basename(file),
                "language": "python",
                "loc": loc,
                "score": final_score,
                "breakdown": breakdown,
                "security_issues": security_data.get("issues", []),
                "optimization_issues": optimization_data.get("issues", []),
            })

        # -------------------------
        # Overall Score
        # -------------------------

        overall_score = round(
            sum(f["score"] for f in file_results) / len(file_results),
            2
        ) if file_results else 0

        software_metrics = {
            "Files Analyzed": len(file_results),
            "Average Score": overall_score,
            "Language": "Python",
            "Dependency Scan": "Enabled" if dependencies else "Not Found"
        }

        return overall_score, file_results, software_metrics

    finally:
        CleanupManager.remove_file(zip_path)
        CleanupManager.remove_directory(extract_path)
