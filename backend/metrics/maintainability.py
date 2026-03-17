import re
import ast
from collections import Counter
from backend.metrics.complexity import calculate_cyclomatic_complexity


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def _get_module_complexity(code: str) -> int:
    """
    Extract integer complexity from enterprise analyzer.
    """
    report = calculate_cyclomatic_complexity(code)

    if isinstance(report, dict):
        return report.get("module_complexity", 0)

    return report or 0


def _get_functions(tree):
    return [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


# --------------------------------------------------
# Readability Checks
# --------------------------------------------------

def _check_naming(tree):
    """
    Basic naming convention checks.
    - functions -> snake_case
    - classes -> PascalCase
    """

    penalty = 0.0

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):
            if not re.match(r"^[a-z_][a-z0-9_]*$", node.name):
                penalty += 0.02

        if isinstance(node, ast.ClassDef):
            if not re.match(r"^[A-Z][A-Za-z0-9]+$", node.name):
                penalty += 0.02

    return penalty


def _check_indentation(code):
    """
    Penalize mixed tabs/spaces and inconsistent indentation.
    """
    penalty = 0.0

    if "\t" in code and "    " in code:
        penalty += 0.05

    lines = code.split("\n")

    for line in lines:
        if line.startswith(" "):
            if len(line) - len(line.lstrip(" ")) % 4 != 0:
                penalty += 0.001

    return penalty


def _comment_coverage(code, loc):
    comment_lines = len(re.findall(r"#|//", code))
    return comment_lines / loc if loc else 0


# --------------------------------------------------
# Structural Complexity
# --------------------------------------------------

def _max_nesting_depth(tree):
    """
    Measures nested control flow depth.
    """

    max_depth = 0

    def visit(node, depth=0):
        nonlocal max_depth
        max_depth = max(max_depth, depth)

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                visit(child, depth + 1)
            else:
                visit(child, depth)

    visit(tree)
    return max_depth


def _function_size_penalty(functions):
    """
    Penalize very large functions.
    """

    penalty = 0.0

    for fn in functions:
        size = getattr(fn, "end_lineno", fn.lineno) - fn.lineno

        if size > 200:
            penalty += 0.05
        elif size > 100:
            penalty += 0.02

    return penalty


# --------------------------------------------------
# Duplication Detection (simple heuristic)
# --------------------------------------------------

def _duplication_penalty(code):
    """
    Detect repeated code blocks using line frequency.
    Lightweight but effective.
    """

    lines = [
        l.strip()
        for l in code.split("\n")
        if l.strip() and not l.strip().startswith("#")
    ]

    counts = Counter(lines)

    repeated = sum(c - 1 for c in counts.values() if c > 3)

    if repeated > 50:
        return 0.1
    if repeated > 20:
        return 0.05
    return 0.0


# --------------------------------------------------
# Public API
# --------------------------------------------------

def calculate_maintainability(code: str, loc: int):
    """
    Enterprise maintainability scoring.

    Measures:
    - Readability
    - Naming conventions
    - Formatting / indentation
    - Documentation coverage
    - Cyclomatic complexity
    - Nesting depth
    - Function size
    - Code duplication
    - Code size
    """

    if loc == 0:
        return 1.0

    try:
        tree = ast.parse(code)
    except:
        return 0.5

    score = 1.0

    # --------------------------------------------------
    # Complexity
    # --------------------------------------------------

    module_complexity = _get_module_complexity(code)

    if module_complexity > 50:
        score -= 0.2
    elif module_complexity > 25:
        score -= 0.1

    # nesting depth
    nesting = _max_nesting_depth(tree)
    if nesting > 6:
        score -= 0.1
    elif nesting > 4:
        score -= 0.05

    # --------------------------------------------------
    # Code size
    # --------------------------------------------------

    if loc > 1000:
        score -= 0.15
    elif loc > 500:
        score -= 0.1

    # --------------------------------------------------
    # Function size
    # --------------------------------------------------

    functions = _get_functions(tree)
    score -= _function_size_penalty(functions)

    # --------------------------------------------------
    # Readability
    # --------------------------------------------------

    score -= _check_naming(tree)
    score -= _check_indentation(code)

    # comment / documentation coverage
    comment_ratio = _comment_coverage(code, loc)
    if comment_ratio > 0.2:
        score += 0.05
    elif comment_ratio < 0.05:
        score -= 0.05

    # --------------------------------------------------
    # Duplication
    # --------------------------------------------------

    score -= _duplication_penalty(code)

    # --------------------------------------------------
    return max(0.5, min(score, 1.0))
