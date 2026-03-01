"""
security.py
------------------------------------
Static security analyzer for Python code.

Checks:
1. Input Handling
   - SQL Injection
   - Command Injection
   - XSS vulnerabilities

2. Authentication & Authorization
   - Hardcoded secrets
   - Weak cryptography / hashing

3. Resource Management
   - File descriptor leaks
   - Socket leaks

4. Sensitive Data Exposure
   - Logging secrets
   - Debug enabled in production

5. Dependency Risks
   - Vulnerable third-party libraries (basic static check)

NOTE:
This is heuristic-based detection, not full security analysis.
"""

import ast
import re


# ==========================================
# MAIN SECURITY EVALUATOR
# ==========================================
def calculate_security(code, dependencies=None):
    """
    Main security scoring function.

    Args:
        code (str): source code string
        dependencies (list or str): optional dependency list (requirements.txt style)

    Returns:
        dict -> {score, issues}
    """

    issues = []
    score = 1.0

    try:
        tree = ast.parse(code)
    except Exception:
        return {"score": 0.3, "issues": ["syntax_error"]}

    # Run all security checks
    issues += check_input_handling(tree, code)
    issues += check_authentication_security(tree)
    issues += check_resource_management(tree)
    issues += check_sensitive_data_exposure(tree, code)

    if dependencies:
        issues += check_dependency_risks(dependencies)

    # scoring system
    penalty_map = {
        "sql_injection": 0.25,
        "command_injection": 0.25,
        "xss_risk": 0.2,
        "hardcoded_secret": 0.4,
        "weak_hashing": 0.3,
        "file_not_closed": 0.2,
        "socket_not_closed": 0.2,
        "logging_sensitive_data": 0.3,
        "debug_enabled": 0.2,
        "vulnerable_dependency": 0.3,
    }

    for issue in issues:
        score -= penalty_map.get(issue, 0.1)

    return {
        "score": max(0.0, round(score, 2)),
        "issues": list(set(issues))  # remove duplicates
    }


# ==========================================
# 1. INPUT HANDLING CHECKS
# ==========================================
def check_input_handling(tree, code):
    """
    Detect:
    - SQL injection patterns
    - Command injection
    - XSS risks
    """
    issues = []

    # --- SQL Injection Detection ---
    # string formatting inside SQL queries
    sql_patterns = [
        r"execute\(.+%s",
        r"execute\(.+format\(",
        r"SELECT .* \+",
        r"INSERT .* \+",
        r"UPDATE .* \+",
    ]

    for pattern in sql_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append("sql_injection")

    # --- Command Injection ---
    # subprocess/os calls with shell=True
    if re.search(r"subprocess\..*shell\s*=\s*True", code):
        issues.append("command_injection")

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ["system", "popen"]:
                    issues.append("command_injection")

    # --- XSS Risk ---
    # unescaped output in web responses
    xss_patterns = [
        r"return\s+request\.",
        r"render\(.+request\.",
        r"html\s*=\s*request\."
    ]

    for pattern in xss_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append("xss_risk")

    return issues


# ==========================================
# 2. AUTHENTICATION & AUTHORIZATION
# ==========================================
def check_authentication_security(tree):
    """
    Detect:
    - Hardcoded passwords/secrets
    - Weak hashing algorithms
    """
    issues = []

    weak_hashes = ["md5", "sha1"]

    for node in ast.walk(tree):

        # --- Hardcoded secrets ---
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value.lower()
            if any(k in value for k in ["password", "secret", "token", "apikey"]):
                issues.append("hardcoded_secret")

        # --- Weak hashing ---
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in weak_hashes:
                    issues.append("weak_hashing")

    return issues


# ==========================================
# 3. RESOURCE MANAGEMENT
# ==========================================
def check_resource_management(tree):
    """
    Detect:
    - Files opened without 'with'
    - Socket usage without close()
    """
    issues = []

    open_calls = 0
    with_open = 0

    for node in ast.walk(tree):

        # count open() calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                open_calls += 1

        # count with open() usage
        if isinstance(node, ast.With):
            for item in node.items:
                if isinstance(item.context_expr, ast.Call):
                    if getattr(item.context_expr.func, "id", None) == "open":
                        with_open += 1

        # socket creation
        if isinstance(node, ast.Attribute):
            if node.attr == "socket":
                issues.append("socket_not_closed")

    if open_calls > with_open:
        issues.append("file_not_closed")

    return issues


# ==========================================
# 4. SENSITIVE DATA EXPOSURE
# ==========================================
def check_sensitive_data_exposure(tree, code):
    """
    Detect:
    - Logging secrets
    - Debug enabled
    """
    issues = []

    # --- Logging sensitive info ---
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ["debug", "info", "warning", "error"]:
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            if any(k in arg.value.lower() for k in ["password", "secret", "token"]):
                                issues.append("logging_sensitive_data")

    # --- Debug mode enabled ---
    if re.search(r"debug\s*=\s*True", code):
        issues.append("debug_enabled")

    return issues


# ==========================================
# 5. DEPENDENCY RISK SCANNING
# ==========================================
def check_dependency_risks(dependencies):
    """
    Very basic static dependency risk check.

    Example input:
        ["django==1.2", "flask==0.9"]
        OR requirements.txt content
    """

    issues = []

    # known vulnerable packages (example list)
    known_vulnerable = {
        "django": ["1.0", "1.1", "1.2"],
        "flask": ["0.9"],
        "pyyaml": ["3.13"],
    }

    if isinstance(dependencies, str):
        dependencies = dependencies.splitlines()

    for dep in dependencies:
        dep = dep.strip().lower()

        for pkg, versions in known_vulnerable.items():
            if dep.startswith(pkg):
                for v in versions:
                    if v in dep:
                        issues.append("vulnerable_dependency")

    return issues
