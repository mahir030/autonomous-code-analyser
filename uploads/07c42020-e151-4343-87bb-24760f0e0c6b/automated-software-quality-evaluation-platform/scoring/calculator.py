def calculate_final_score(metrics):
    total = sum(metrics.values())
    return round(total / len(metrics), 2)

