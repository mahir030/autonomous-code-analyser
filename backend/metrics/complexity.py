import ast
from typing import Dict, List


class ComplexityVisitor(ast.NodeVisitor):
    """
    Enterprise-grade Cyclomatic Complexity Analyzer.

    Complexity rules:
    - Base = 1
    - +1 per decision point
    """

    def __init__(self):
        self.complexity = 1

    # ---- Branching ----

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_IfExp(self, node):  # ternary: x if cond else y
        self.complexity += 1
        self.generic_visit(node)

    # ---- Loops ----

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    # ---- Exception handling ----

    def visit_Try(self, node):
        # each except adds path
        self.complexity += len(node.handlers)

        if node.finalbody:
            self.complexity += 1

        self.generic_visit(node)

    # ---- Boolean logic ----

    def visit_BoolOp(self, node):
        # each extra boolean condition increases paths
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    # ---- Comprehensions ----

    def visit_ListComp(self, node):
        self.complexity += len(node.generators)
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self.complexity += len(node.generators)
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self.complexity += len(node.generators)
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        self.complexity += len(node.generators)
        self.generic_visit(node)


# --------------------------------------------------

def calculate_function_complexity(node: ast.FunctionDef) -> int:
    visitor = ComplexityVisitor()
    visitor.visit(node)
    return visitor.complexity


def calculate_module_complexity(tree: ast.AST) -> Dict:
    """
    Returns enterprise-style report.
    """

    report = {
        "functions": [],
        "module_complexity": 0
    }

    total = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            complexity = calculate_function_complexity(node)

            report["functions"].append({
                "name": node.name,
                "line": node.lineno,
                "complexity": complexity,
                "risk": classify_complexity(complexity)
            })

            total += complexity

    report["module_complexity"] = total or 1
    return report


def classify_complexity(score: int) -> str:
    """
    Enterprise risk classification.
    """

    if score <= 5:
        return "low"
    elif score <= 10:
        return "moderate"
    elif score <= 20:
        return "high"
    return "critical"


# --------------------------------------------------

def calculate_cyclomatic_complexity(code: str) -> Dict:
    """
    Public API.
    """

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "module_complexity": 0,
            "functions": [],
            "error": "syntax_error"
        }

    return calculate_module_complexity(tree)
