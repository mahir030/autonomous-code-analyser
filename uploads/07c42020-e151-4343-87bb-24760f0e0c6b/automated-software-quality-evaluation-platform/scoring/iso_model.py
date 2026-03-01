def iso_quality_model(loc, python_files):
    maintainability = max(0, 100 - (loc // 50))
    portability = min(100, python_files * 10)
    reliability = 80

    return {
        "maintainability": maintainability,
        "portability": portability,
        "reliability": reliability
    }

