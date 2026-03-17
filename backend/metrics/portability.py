import re
import ast


OS_PATTERNS = [
    r"C:\\\\",                  # Windows paths
    r"/usr/bin",                # Linux specific
    r"\.exe\b",                 # Windows binaries
    r"import win32",            # Windows API
    r"os\.system\(",            # shell dependence
]

ENCODING_PATTERNS = [
    r"\.encode\(['\"]ascii['\"]\)",
    r"\.decode\(['\"]ascii['\"]\)",
]

FS_PATTERNS = [
    r"\\\\",                    # hardcoded backslash paths
    r"/home/",                  # linux user path
]

DEPENDENCY_PATTERNS = [
    r"import\s+win32",
    r"import\s+fcntl",
]

DATA_FORMAT_PATTERNS = [
    r"struct\.pack\(",
    r"struct\.unpack\(",
]


def check_python_version_compatibility(tree):
    """
    Detect syntax requiring newer Python versions.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Match):  # Python 3.10+
            return True
    return False


def calculate_portability(code, language="python"):
    if not code.strip():
        return 0.5

    score = 1.0

    # ------------------------------------
    # OS-specific constructs
    # ------------------------------------
    for pattern in OS_PATTERNS:
        if re.search(pattern, code):
            score -= 0.1

    # ------------------------------------
    # File system assumptions
    # ------------------------------------
    for pattern in FS_PATTERNS:
        if re.search(pattern, code):
            score -= 0.05

    # ------------------------------------
    # Encoding assumptions
    # ------------------------------------
    for pattern in ENCODING_PATTERNS:
        if re.search(pattern, code):
            score -= 0.05

    # ------------------------------------
    # External dependencies
    # ------------------------------------
    for pattern in DEPENDENCY_PATTERNS:
        if re.search(pattern, code):
            score -= 0.1

    # ------------------------------------
    # Binary / endianness assumptions
    # ------------------------------------
    for pattern in DATA_FORMAT_PATTERNS:
        if re.search(pattern, code):
            score -= 0.05

    # ------------------------------------
    # Python interpreter compatibility
    # ------------------------------------
    if language.lower() == "python":
        try:
            tree = ast.parse(code)

            if check_python_version_compatibility(tree):
                score -= 0.05

        except Exception:
            score -= 0.2

    return max(0.5, round(score, 2))
