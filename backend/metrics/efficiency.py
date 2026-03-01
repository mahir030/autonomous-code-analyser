import ast
import hashlib


# =========================
# Advanced Efficiency Analyzer
# =========================

class EfficiencyAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        self.loop_depth = 0

        self.assigned_vars = set()
        self.used_vars = set()

        self.loop_assigned_vars_stack = []
        self.loop_expression_hashes = []

        self.expensive_calls = {
            "sleep",
            "open",
            "connect",
            "subprocess",
            "compile",
            "eval",
            "exec"
        }

    # -------------------------
    # Loop Handling
    # -------------------------

    def visit_For(self, node):
        self.loop_depth += 1
        self.loop_assigned_vars_stack.append(set())
        self.loop_expression_hashes.append(set())

        self.generic_visit(node)

        self.loop_assigned_vars_stack.pop()
        self.loop_expression_hashes.pop()
        self.loop_depth -= 1

    def visit_While(self, node):
        self.visit_For(node)  # same logic

    # -------------------------
    # Assignments
    # -------------------------

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assigned_vars.add(target.id)

                if self.loop_depth > 0:
                    self.loop_assigned_vars_stack[-1].add(target.id)

        self.generic_visit(node)

    # -------------------------
    # Variable Usage
    # -------------------------

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_vars.add(node.id)

    # -------------------------
    # Function Calls
    # -------------------------

    def visit_Call(self, node):
        func_name = None

        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        # Heavy operation inside loop
        if self.loop_depth > 0 and func_name in self.expensive_calls:
            self.issues.append("heavy_operation_inside_loop")

        # Object creation inside loop
        if self.loop_depth > 0:
            if isinstance(node.func, ast.Name):
                if node.func.id in {"list", "dict", "set", "tuple"}:
                    self.issues.append("object_creation_inside_loop")

        self.generic_visit(node)

    # -------------------------
    # Binary Operations
    # -------------------------

    def visit_BinOp(self, node):
        if self.loop_depth > 0:
            expr_dump = ast.dump(node)
            expr_hash = hashlib.md5(expr_dump.encode()).hexdigest()

            current_loop_hashes = self.loop_expression_hashes[-1]

            # Repeated computation detection
            if expr_hash in current_loop_hashes:
                self.issues.append("redundant_computation_inside_loop")
            else:
                current_loop_hashes.add(expr_hash)

            # Loop invariant detection
            used_names = {
                n.id for n in ast.walk(node)
                if isinstance(n, ast.Name)
            }

            assigned_in_loop = self.loop_assigned_vars_stack[-1]

            if not used_names.intersection(assigned_in_loop):
                self.issues.append("loop_invariant_computation")

        self.generic_visit(node)


# =========================
# Efficiency Scoring
# =========================

def calculate_efficiency(code, loc):
    if loc == 0:
        return 1.0

    try:
        tree = ast.parse(code)
    except:
        return 0.3

    analyzer = EfficiencyAnalyzer()
    analyzer.visit(tree)

    issues = analyzer.issues

    # Unused variable detection
    unused_vars = analyzer.assigned_vars - analyzer.used_vars
    if unused_vars:
        issues.append("unused_variables")

    # -------------------------
    # Scoring Model
    # -------------------------

    score = 1.0

    penalty_weights = {
        "heavy_operation_inside_loop": 0.1,
        "object_creation_inside_loop": 0.08,
        "redundant_computation_inside_loop": 0.07,
        "loop_invariant_computation": 0.07,
        "unused_variables": 0.05
    }

    for issue in issues:
        score -= penalty_weights.get(issue, 0.05)

    return max(score, 0.1)
