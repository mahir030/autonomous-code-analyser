import ast
import re

# Tree-sitter optional
try:
    from tree_sitter_languages import get_parser
    TREE_SITTER_AVAILABLE = True
except:
    TREE_SITTER_AVAILABLE = False


# -------------------------
# Python AST Reliability Check
# -------------------------

class PythonReliabilityAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        self.try_blocks = 0
        self.functions = 0

    def visit_FunctionDef(self, node):
        self.functions += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        self.try_blocks += 1

        # bare except detection
        for handler in node.handlers:
            if handler.type is None:
                self.issues.append({
                    "type": "bare_except",
                    "severity": 0.25,
                    "message": "Bare except reduces reliability"
                })

        self.generic_visit(node)


def analyze_python_reliability(code):
    try:
        tree = ast.parse(code)
    except:
        return 0.3, [{"type": "syntax_error"}]

    analyzer = PythonReliabilityAnalyzer()
    analyzer.visit(tree)

    score = 1.0

    if analyzer.functions > 0 and analyzer.try_blocks == 0:
        score -= 0.3
        analyzer.issues.append({
            "type": "no_error_handling",
            "severity": 0.3
        })

    for issue in analyzer.issues:
        score -= issue["severity"]

    return max(0, score), analyzer.issues


# -------------------------
# Universal Language Checks
# -------------------------

def universal_reliability_checks(code):
    issues = []
    score = 1.0

    # infinite loop risk
    if re.search(r"while\s*\(\s*true\s*\)|while\s+True", code):
        issues.append({"type": "infinite_loop", "severity": 0.3})
        score -= 0.3

    # magic numbers
    if len(re.findall(r"\b\d{3,}\b", code)) > 5:
        issues.append({"type": "magic_numbers", "severity": 0.1})
        score -= 0.1

    # deep nesting heuristic
    if code.count("{") > 50 or code.count("if") > 40:
        issues.append({"type": "deep_nesting", "severity": 0.2})
        score -= 0.2

    # no error handling indicators
    error_keywords = ["try", "catch", "except", "error", "fail"]
    if not any(k in code.lower() for k in error_keywords):
        issues.append({"type": "no_error_handling_detected", "severity": 0.25})
        score -= 0.25

    return max(0, score), issues


# -------------------------
# Tree-sitter Multi-language Check
# -------------------------

def tree_sitter_reliability(code, language="python"):
    if not TREE_SITTER_AVAILABLE:
        return 1.0, []

    try:
        parser = get_parser(language.lower())
        tree = parser.parse(bytes(code, "utf8"))
        root = tree.root_node

        function_count = 0
        node_stack = [root]

        while node_stack:
            node = node_stack.pop()
            if "function" in node.type:
                function_count += 1
            node_stack.extend(node.children)

        score = 1.0
        issues = []

        if function_count > 0 and "try" not in code.lower():
            score -= 0.2
            issues.append({
                "type": "no_error_handling_structure",
                "severity": 0.2
            })

        return max(0, score), issues

    except:
        return 1.0, []


# -------------------------
# Main API (used by evaluator)
# -------------------------

def calculate_reliability(code_string, language="python"):
    """
    Returns reliability score 0-1
    """

    if not code_string:
        return 0.5

    scores = []

    # universal checks (always run)
    universal_score, _ = universal_reliability_checks(code_string)
    scores.append(universal_score)

    # python deep analysis
    if language.lower() == "python":
        python_score, _ = analyze_python_reliability(code_string)
        scores.append(python_score)

    # multi-language AST check
    ts_score, _ = tree_sitter_reliability(code_string, language)
    scores.append(ts_score)

    return round(sum(scores) / len(scores), 2)
