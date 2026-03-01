import os

def count_loc(path):
    total = 0
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith((".py", ".js", ".html", ".css")):
                with open(os.path.join(root, file), "r", errors="ignore") as f:
                    total += len(f.readlines())
    return total

