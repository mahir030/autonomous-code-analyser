from backend.config import ISO_WEIGHTS

def compute_iso_score(metrics):
    scores = {
        "functional_suitability": min(metrics["loc"] / 100, 1),
        "performance_efficiency": 0.8,
        "compatibility": 0.7,
        "usability": 0.75,
        "reliability": 0.85,
        "security": 0.7,
        "maintainability": 1 - min(metrics["loc"] / 500, 1),
        "portability": 0.9
    }

    total = 0
    for k, v in scores.items():
        total += v * ISO_WEIGHTS[k]

    return round(total * 100, 2), scores

