import ast


def calculate_optimization(code):
    """
    Static optimization analysis.

    Checks:
    - algorithmic inefficiency (nested loops)
    - redundant operations
    - memory inefficiency
    - unused variables
    - object creation inside loops
    """

    try:
        tree = ast.parse(code)
    except:
        return {"score": 0.4, "issues": ["syntax_error"]}

    issues = []

    analyzer = OptimizationAnalyzer()
    analyzer.visit(tree)

    issues.extend(analyzer.issues)

    # scoring logic
    score = 1.0

    penalties = {
        "nested_loops": 0.15,
        "redundant_function_call": 0.1,
        "object_creation_in_loop": 0.1,
        "unused_variable": 0.05,
        "inefficient_list_building": 0.1,
    }

    for issue in issues:
        score -= penalties.get(issue, 0.05)

    return {
        "score": max(score, 0.3),
        "issues": list(set(issues))
    }


class OptimizationAnalyzer(ast.NodeVisitor):

    def __init__(self):
        self.issues = []
        self.loop_depth = 0
        self.assigned = set()
        self.used = set()

    # -------------------------
    # Loop analysis (algorithmic cost)
    # -------------------------

    def visit_For(self, node):
        self.loop_depth += 1

        if self.loop_depth >= 2:
            self.issues.append("nested_loops")

        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node):
        self.loop_depth += 1

        if self.loop_depth >= 2:
            self.issues.append("nested_loops")

        self.generic_visit(node)
        self.loop_depth -= 1

    # -------------------------
    # Memory inefficiency
    # -------------------------

    def visit_Call(self, node):
        if self.loop_depth > 0:
            if isinstance(node.func, ast.Name):
                if node.func.id in ["list", "dict", "set", "tuple"]:
                    self.issues.append("object_creation_in_loop")

        self.generic_visit(node)

    # -------------------------
    # Inefficient list building
    # list.append inside loop instead of comprehension
    # -------------------------

    def visit_Attribute(self, node):
        if self.loop_depth > 0 and node.attr == "append":
            self.issues.append("inefficient_list_building")

        self.generic_visit(node)

    # -------------------------
    # Unused variables
    # -------------------------

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.assigned.add(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.used.add(node.id)

    def finalize(self):
        unused = self.assigned - self.used
        if unused:
            self.issues.append("unused_variable")
