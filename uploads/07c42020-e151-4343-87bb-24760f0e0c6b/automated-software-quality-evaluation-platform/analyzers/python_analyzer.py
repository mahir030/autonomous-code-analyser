import os

def python_file_count(path):
    count = 0
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                count += 1
    return count

