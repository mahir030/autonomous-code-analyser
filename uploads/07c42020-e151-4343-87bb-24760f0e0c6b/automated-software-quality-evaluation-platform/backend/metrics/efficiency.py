def calculate_efficiency(loc):
    if loc < 200:
        return 0.9
    elif loc < 1000:
        return 0.75
    return 0.6

