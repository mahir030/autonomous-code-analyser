import os

EXTENSION_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".sh": "Bash"
}

def detect_language(filename):
    ext = os.path.splitext(filename)[1]
    return EXTENSION_MAP.get(ext, "Unknown")

