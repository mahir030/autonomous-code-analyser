import os

def calculate_loc(file_path):
    with open(file_path, "r", errors="ignore") as f:
        return len([line for line in f if line.strip()])

