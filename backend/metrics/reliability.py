import ast
import re


class ReliabilityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.has_try = False
        self.unreachable_code = False
        self.used_vars = set()
        self.assigned_vars = set()
        self.none_risk = False

    # ---- Error handling ----
    def visit_Try(self, node):
        self.has_try = True
        self.generic_visit(node)

    # ---- Variable assignment tracking ----
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assigned_vars.add(target.id)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_vars.add(node.id)

    # ---- None dereference risk ----
    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            if node.value.id not in self.assigned_vars:
                self.none_risk = True
        self.generic_visit(node)

    # ---- Unreachable code ----
    def visit_Return(self, node):
        self.unreachable_code = True

    def visit_Raise(self, node):
        self.unreachable_code = True


def calculate_reliability(code, language="python"):
    if not code.strip():
        return 0.5

    score = 1.0

    # ------------------------------------
    # Infinite loop risk
    # ------------------------------------
    if re.search(r"while\s*\(\s*true\s*\)|while\s+True", code):
        score -= 0.25

    # ------------------------------------
    # Magic numbers
    # ------------------------------------
    if len(re.findall(r"\b\d{3,}\b", code)) > 5:
        score -= 0.05

    # ------------------------------------
    # Boundary / off-by-one risks
    # ------------------------------------
    if re.search(r"range\s*\(.*len\(.*\)\)", code):
        score -= 0.05

    # ------------------------------------
    # Python AST analysis
    # ------------------------------------
    if language.lower() == "python":
        try:
            tree = ast.parse(code)
            visitor = ReliabilityVisitor()
            visitor.visit(tree)

            # Missing exception handling
            if not visitor.has_try:
                score -= 0.2

            # Variable used before assignment
            undefined = visitor.used_vars - visitor.assigned_vars
            if undefined:
                score -= 0.15

            # None dereference risk
            if visitor.none_risk:
                score -= 0.1

            # Unreachable code
            if visitor.unreachable_code:
                score -= 0.05

        except Exception:
            score -= 0.4

    return max(0.5, round(score, 2))
