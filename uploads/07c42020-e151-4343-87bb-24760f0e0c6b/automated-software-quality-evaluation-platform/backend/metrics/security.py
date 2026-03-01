import ast
import re


class SecurityAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []

    # Detect dangerous function calls
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            dangerous_funcs = {
                "eval": "Code execution risk",
                "exec": "Code execution risk",
                "compile": "Dynamic code execution",
                "input": "User input risk",
            }

            if node.func.id in dangerous_funcs:
                self.issues.append({
                    "type": "dangerous_function",
                    "name": node.func.id,
                    "severity": 0.25,
                    "message": dangerous_funcs[node.func.id]
                })

        # Detect os.system / subprocess calls
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ["system", "popen", "run", "call"]:
                self.issues.append({
                    "type": "command_execution",
                    "name": node.func.attr,
                    "severity": 0.3,
                    "message": "Possible command injection"
                })

        self.generic_visit(node)

    # Detect hardcoded strings (possible secrets)
    def visit_Assign(self, node):
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            value = node.value.value.lower()

            secret_keywords = ["password", "secret", "token", "api_key", "apikey"]

            for keyword in secret_keywords:
                if keyword in value:
                    self.issues.append({
                        "type": "hardcoded_secret",
                        "severity": 0.4,
                        "message": "Possible hardcoded secret"
                    })

        self.generic_visit(node)


def check_regex_security(code):
    """
    Extra checks AST cannot easily detect.
    """
    issues = []

    patterns = {
        r"pickle\.loads": ("Unsafe deserialization", 0.35),
        r"yaml\.load\(": ("Unsafe YAML load", 0.35),
        r"subprocess\..*\(.*shell=True": ("Shell injection risk", 0.4),
    }

    for pattern, (msg, severity) in patterns.items():
        if re.search(pattern, code):
            issues.append({
                "type": "pattern_match",
                "severity": severity,
                "message": msg
            })

    return issues


def calculate_security(code_string):
    """
    Returns:
        {
            "score": float (0 to 1),
            "issues": list
        }
    """

    try:
        tree = ast.parse(code_string)
    except SyntaxError:
        return {
            "score": 0,
            "issues": [{"type": "syntax_error"}]
        }

    analyzer = SecurityAnalyzer()
    analyzer.visit(tree)

    regex_issues = check_regex_security(code_string)

    all_issues = analyzer.issues + regex_issues

    # Score calculation
    score = 1.0
    for issue in all_issues:
        score -= issue["severity"]

    score = max(0, round(score, 2))

    return {
        "score": score,
        "issues": all_issues
    }
