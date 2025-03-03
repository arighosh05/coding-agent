from typing import Callable, Dict, List, Tuple, Set, Optional
import re
import ast
import builtins
import keyword

# A mapping from aspect names to functions that analyze the code.
TOOL_MAPPING: Dict[str, Callable[[str], str]] = {}

def register_tool(aspect: str, func: Callable[[str], str]) -> None:
    """
    Register a tool function for a given code analysis aspect.
    """
    TOOL_MAPPING[aspect] = func

def get_tool_by_aspect(aspect: str) -> Callable[[str], str]:
    """
    Retrieve the tool function registered for a specific aspect.
    Returns None if no tool is registered.
    """
    return TOOL_MAPPING.get(aspect)

# Helper functions for static analysis

def safe_parse(code: str) -> Optional[ast.AST]:
    """Safely parse Python code into an AST."""
    try:
        return ast.parse(code)
    except SyntaxError:
        return None

def count_nested_loops(node: ast.AST) -> int:
    """Count the maximum nesting level of loops."""
    if isinstance(node, (ast.For, ast.While)):
        return 1 + max([count_nested_loops(child) for child in ast.iter_child_nodes(node)], default=0)
    return max([count_nested_loops(child) for child in ast.iter_child_nodes(node)], default=0)

def find_recursive_calls(node: ast.AST, function_name: Optional[str] = None) -> List[str]:
    """Find recursive function calls in the code."""
    recursive_functions = []

    class RecursiveCallVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_function = None
            self.recursive_functions = set()

        def visit_FunctionDef(self, node):
            old_function = self.current_function
            self.current_function = node.name
            self.generic_visit(node)
            self.current_function = old_function

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id == self.current_function:
                self.recursive_functions.add(self.current_function)
            self.generic_visit(node)

    visitor = RecursiveCallVisitor()
    visitor.visit(node)
    return list(visitor.recursive_functions)

def find_exception_handlers(node: ast.AST) -> int:
    """Count exception handlers in the code."""
    class ExceptionVisitor(ast.NodeVisitor):
        def __init__(self):
            self.exception_count = 0

        def visit_Try(self, node):
            self.exception_count += len(node.handlers)
            self.generic_visit(node)

    visitor = ExceptionVisitor()
    visitor.visit(node)
    return visitor.exception_count

def analyze_variable_names(node: ast.AST) -> Tuple[List[str], List[str]]:
    """Analyze variable names for clarity."""
    class VariableVisitor(ast.NodeVisitor):
        def __init__(self):
            self.variables = set()

        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Store):
                self.variables.add(node.id)
            self.generic_visit(node)

        def visit_arg(self, node):
            self.variables.add(node.arg)
            self.generic_visit(node)

    visitor = VariableVisitor()
    visitor.visit(node)

    # Identify poor variable names
    poor_names = []
    good_names = []

    for var in visitor.variables:
        if len(var) <= 1 and var not in ['i', 'j', 'k', 'n', 'm', 'x', 'y', 'z']:
            poor_names.append(var)
        elif var.lower() in ['temp', 'tmp', 'var', 'foo', 'bar']:
            poor_names.append(var)
        elif re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', var) and len(var) > 2:
            good_names.append(var)

    return good_names, poor_names

def detect_security_issues(code: str, tree: ast.AST) -> List[str]:
    """Detect potential security issues in the code."""
    issues = []

    # Check for dangerous eval/exec
    if "eval(" in code or "exec(" in code:
        issues.append("Use of eval() or exec() detected, which can execute arbitrary code")

    # Check for SQL injection potential
    if re.search(r'cursor\.execute\(.*?\+.*?\)', code) or re.search(r'execute\(.*?\%.*?\)', code):
        issues.append("Potential SQL injection detected - string concatenation in SQL query")

    # Check for hardcoded credentials
    if re.search(r'password\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE) or re.search(r'api_key\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE):
        issues.append("Hardcoded credentials detected (password or API key)")

    # Check for shell injection
    if re.search(r'os\.system\(.*?\+.*?\)', code) or re.search(r'subprocess\.call\(.*?\+.*?\)', code):
        issues.append("Potential command injection in os.system() or subprocess calls")

    return issues

def find_unnecessary_nesting(node: ast.AST) -> int:
    """Find unnecessary levels of nesting."""
    class NestingVisitor(ast.NodeVisitor):
        def __init__(self):
            self.max_nesting = 0
            self.current_nesting = 0

        def visit_If(self, node):
            self.current_nesting += 1
            self.max_nesting = max(self.max_nesting, self.current_nesting)
            self.generic_visit(node)
            self.current_nesting -= 1

        def visit_For(self, node):
            self.current_nesting += 1
            self.max_nesting = max(self.max_nesting, self.current_nesting)
            self.generic_visit(node)
            self.current_nesting -= 1

        def visit_While(self, node):
            self.current_nesting += 1
            self.max_nesting = max(self.max_nesting, self.current_nesting)
            self.generic_visit(node)
            self.current_nesting -= 1

    visitor = NestingVisitor()
    visitor.visit(node)
    return visitor.max_nesting

def check_scalability_issues(node: ast.AST) -> List[str]:
    """Identify potential scalability bottlenecks."""
    issues = []

    # Check for global variables which could be bottlenecks
    globals_used = set()

    class GlobalVisitor(ast.NodeVisitor):
        def visit_Global(self, node):
            for name in node.names:
                globals_used.add(name)
            self.generic_visit(node)

    visitor = GlobalVisitor()
    visitor.visit(node)

    if globals_used:
        issues.append(f"Global variables that may affect scalability: {', '.join(globals_used)}")

    # Check for potential bottlenecks in loops
    nested_loops = count_nested_loops(node)
    if nested_loops > 1:
        issues.append(f"Found {nested_loops} levels of nested loops which may affect performance at scale")

    return issues

def find_class_structures(node: ast.AST) -> List[str]:
    """Analyze class structures for extensibility."""
    class ClassVisitor(ast.NodeVisitor):
        def __init__(self):
            self.classes = []
            self.inheritance = {}

        def visit_ClassDef(self, node):
            self.classes.append(node.name)
            self.inheritance[node.name] = [base.id if isinstance(base, ast.Name) else "unknown" for base in node.bases]
            self.generic_visit(node)

    visitor = ClassVisitor()
    visitor.visit(node)

    insights = []
    if visitor.classes:
        insights.append(f"Found {len(visitor.classes)} classes: {', '.join(visitor.classes)}")

        for cls, bases in visitor.inheritance.items():
            if bases:
                insights.append(f"Class {cls} inherits from: {', '.join(bases)}")

    return insights

def find_potential_imports(code: str) -> List[str]:
    """Identify potential dependencies by analyzing imports."""
    imports = []
    tree = safe_parse(code)

    if tree:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

    return imports

# -------------------------------
#  Tool functions implementation
# -------------------------------

def analyze_time_complexity(code: str) -> str:
    """Analyze time complexity of the provided code."""
    tree = safe_parse(code)
    if not tree:
        return "Unable to parse code for time complexity analysis."

    # Check for nested loops (indicating potential O(n^2) or worse)
    max_loop_depth = count_nested_loops(tree)

    # Check for recursive functions (potentially exponential)
    recursive_functions = find_recursive_calls(tree)

    complexity_analysis = []

    if max_loop_depth == 0:
        complexity_analysis.append("No loops detected. Time complexity may be O(1) if there are no other scaling operations.")
    elif max_loop_depth == 1:
        complexity_analysis.append("Single loop detected. Possible O(n) time complexity.")
    elif max_loop_depth == 2:
        complexity_analysis.append("Two nested loops detected. Possible O(n²) time complexity.")
    elif max_loop_depth > 2:
        complexity_analysis.append(f"{max_loop_depth} levels of nested loops detected. Possible O(n^{max_loop_depth}) time complexity.")

    if recursive_functions:
        complexity_analysis.append(f"Recursive functions detected: {', '.join(recursive_functions)}. "
                                   f"This might lead to exponential time complexity if not carefully implemented.")

    # Check for built-in operations with known complexities
    if "sort(" in code or "sorted(" in code:
        complexity_analysis.append("Sorting operations detected (sort/sorted). These typically have O(n log n) complexity.")

    if re.search(r'\.index\(|\.find\(', code):
        complexity_analysis.append("Linear search operations detected (.index() or .find()). These typically have O(n) complexity.")

    if " in " in code and ("[" in code or "list" in code.lower()):
        complexity_analysis.append("'in' operator on lists detected. This has O(n) complexity. Consider using a set or dict for O(1) lookups if appropriate.")

    return "\n".join(complexity_analysis)


def analyze_space_complexity(code: str) -> str:
    """Analyze space complexity of the provided code."""
    tree = safe_parse(code)
    if not tree:
        return "Unable to parse code for space complexity analysis."

    space_analysis = []

    # Look for data structures
    list_usage = len(re.findall(r'\[\s*\]|\blist\s*\(', code))
    dict_usage = len(re.findall(r'\{\s*\}|\bdict\s*\(', code))
    set_usage = len(re.findall(r'\{\s*\}|\bset\s*\(', code))

    # Count potential array accumulations
    append_count = len(re.findall(r'\.append\(', code))
    extend_count = len(re.findall(r'\.extend\(', code))
    accumulation_count = append_count + extend_count

    if list_usage > 0 or dict_usage > 0 or set_usage > 0:
        space_analysis.append(f"Data structure usage detected: {list_usage} list(s), {dict_usage} dict(s), {set_usage} set(s).")

    if accumulation_count > 0:
        space_analysis.append(f"Found {accumulation_count} instances of list growth operations (.append/.extend), which may increase space usage linearly.")

    # Check for recursive calls (could lead to stack growth)
    recursive_functions = find_recursive_calls(tree)
    if recursive_functions:
        space_analysis.append(f"Recursive functions detected: {', '.join(recursive_functions)}. This will consume stack space proportional to recursion depth.")

    # Check for comprehensions (temporary space)
    comprehensions = len(re.findall(r'\[\s*\w+\s+for', code))
    if comprehensions > 0:
        space_analysis.append(f"Found {comprehensions} list comprehension(s), which create temporary data structures.")

    # Overall assessment
    if not space_analysis:
        space_analysis.append("No significant space complexity concerns detected. Space usage appears to be O(1) constant.")
    else:
        space_analysis.append("Based on data structure usage, the space complexity may be O(n) linear with input size.")

    return "\n".join(space_analysis)


def analyze_edge_cases(code: str) -> str:
    """Identify potential edge cases the code might not handle properly."""
    tree = safe_parse(code)
    if not tree:
        return "Unable to parse code for edge case analysis."

    edge_cases = []

    # Check for division operations (potential divide by zero)
    if "/" in code or "//" in code:
        edge_cases.append("Division operations detected without visible checks for division by zero.")

    # Check for list/array indexing (potential index out of bounds)
    if "[" in code and "]" in code:
        edge_cases.append("Array indexing detected. Check for potential index out of bounds errors with empty lists or invalid indices.")

    # Check for null/None checks
    none_checks = len(re.findall(r'is None|is not None|== None|!= None', code))
    if none_checks == 0 and "None" not in code:
        edge_cases.append("No None checks detected. Consider handling None values as inputs or in calculations.")

    # Check for error handling
    exception_count = find_exception_handlers(tree) if tree else 0
    if exception_count == 0:
        edge_cases.append("No exception handling detected. Consider adding try/except blocks for potential runtime errors.")

    # Check for empty collections handling
    empty_checks = len(re.findall(r'if\s+len\s*\(\s*\w+\s*\)\s*[=><!]=?\s*0', code))
    if empty_checks == 0 and ("list" in code.lower() or "[]" in code or "{}" in code):
        edge_cases.append("No checks for empty collections detected. Consider handling empty lists, dictionaries, or strings.")

    # Input validation
    if "def " in code and "if " not in code:
        edge_cases.append("Function defined without conditional statements. Consider adding input validation.")

    # Special case for recursion base cases
    recursive_funcs = find_recursive_calls(tree) if tree else []
    if recursive_funcs and "return" in code:
        edge_cases.append(f"Recursive functions detected: {', '.join(recursive_funcs)}. Ensure proper base cases exist to prevent infinite recursion.")

    if not edge_cases:
        edge_cases.append("No obvious edge cases detected in static analysis.")

    return "\n".join(edge_cases)


def analyze_code_clarity(code: str) -> str:
    """Evaluate code readability and maintainability."""
    tree = safe_parse(code)
    if not tree:
        return "Unable to parse code for clarity analysis."

    clarity_analysis = []

    # Check variable names
    good_names, poor_names = analyze_variable_names(tree)
    if poor_names:
        clarity_analysis.append(f"Found {len(poor_names)} potentially unclear variable names: {', '.join(poor_names)}")

    # Check for comments
    comment_lines = re.findall(r'#.*$', code, re.MULTILINE)
    comment_ratio = len(comment_lines) / max(1, len(code.split('\n')))
    docstrings = re.findall(r'""".*?"""', code, re.DOTALL)

    if comment_ratio < 0.1 and not docstrings:
        clarity_analysis.append("Low comment density detected. Consider adding more explanatory comments.")

    # Check for docstrings
    if "def " in code and not docstrings:
        clarity_analysis.append("Functions detected without docstrings. Consider adding documentation for functions.")

    # Check for overly complex statements
    long_lines = [line for line in code.split('\n') if len(line.strip()) > 80]
    if long_lines:
        clarity_analysis.append(f"Found {len(long_lines)} lines longer than 80 characters, which may reduce readability.")

    # Check for excessive nesting
    nesting_level = find_unnecessary_nesting(tree)
    if nesting_level > 3:
        clarity_analysis.append(f"Deep nesting detected (level {nesting_level}). Consider refactoring nested blocks into separate functions.")

    # Check for magic numbers
    magic_numbers = re.findall(r'[^_a-zA-Z0-9"\'](\d+)[^_a-zA-Z0-9]', code)
    if len(magic_numbers) > 3:
        clarity_analysis.append(f"Found {len(magic_numbers)} potential magic numbers. Consider using named constants.")

    if not clarity_analysis:
        clarity_analysis.append("Code appears to be relatively clear and well-structured based on static analysis.")

    return "\n".join(clarity_analysis)


def analyze_security(code: str) -> str:
    """Identify security vulnerabilities in the code."""
    tree = safe_parse(code)
    security_issues = []

    if tree:
        security_issues = detect_security_issues(code, tree)

    # Additional checks

    # Check for insecure hash algorithms
    if re.search(r'import\s+md5|import\s+sha1|hashlib\.md5|hashlib\.sha1', code):
        security_issues.append("Use of weak hash algorithms (MD5/SHA1) detected. Consider using SHA-256 or better.")

    # Check for potential path traversal
    if re.search(r'open\s*\(\s*[\'"](\.\.\/|~\/|\/)[\'"]', code) or re.search(r'open\s*\(\s*\w+\s*\+', code):
        security_issues.append("Potential path traversal vulnerability detected in file operations.")

    # Check for CSRF protection
    if "django" in code.lower() and "csrf" not in code.lower():
        security_issues.append("Django code detected without visible CSRF protection.")

    # Check for potential XSS
    if re.search(r'\.html\s*\(|safe\s*\(|mark_safe', code) and re.search(r'\+\s*\w+|\{\{\s*\w+\s*\}\}', code):
        security_issues.append("Potential XSS vulnerability: unescaped variables in HTML content.")

    # Check for TLS/SSL verification skipping
    if "verify=False" in code or "CERT_NONE" in code:
        security_issues.append("SSL/TLS certificate verification disabled, creating potential MITM vulnerability.")

    if not security_issues:
        security_issues.append("No obvious security vulnerabilities detected in static analysis.")

    return "\n".join(security_issues)


def analyze_correctness(code: str) -> str:
    """Identify logical errors or bugs in the code."""
    tree = safe_parse(code)
    if not tree:
        return "Unable to parse code for correctness analysis."

    correctness_issues = []

    # Check for common edge case bugs

    # Off-by-one errors in range/loops
    for_loops = re.findall(r'for\s+\w+\s+in\s+range\s*\(\s*[^,)]+\s*,\s*([^,)]+)\s*\)', code)
    for loop_end in for_loops:
        if loop_end.strip() in ['len(s)', 'len(arr)', 'len(list)', 'len(input)']:
            correctness_issues.append(f"Potential off-by-one error in loop with range({loop_end}). "
                                      "Check if range should end at len()-1.")

    # Uninitialized variables
    class UninitializedVarVisitor(ast.NodeVisitor):
        def __init__(self):
            self.defined = set()
            self.used = set()

        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Store):
                self.defined.add(node.id)
            elif isinstance(node.ctx, ast.Load) and node.id not in dir(builtins) and not keyword.iskeyword(node.id):
                self.used.add(node.id)
            self.generic_visit(node)

    visitor = UninitializedVarVisitor()
    visitor.visit(tree)

    potentially_uninitialized = visitor.used - visitor.defined
    if potentially_uninitialized:
        # Filter out likely imports or builtin functions
        filtered = [v for v in potentially_uninitialized if not v[0].isupper() and v not in ['self', 'cls']]
        if filtered:
            correctness_issues.append(f"Potentially uninitialized variables: {', '.join(filtered)}")

    # Check for unreachable code after return
    class ReturnVisitor(ast.NodeVisitor):
        def __init__(self):
            self.has_unreachable = False

        def visit_FunctionDef(self, node):
            statements_after_return = False
            has_return = False

            for stmt in node.body:
                if isinstance(stmt, ast.Return):
                    has_return = True
                elif has_return:
                    statements_after_return = True
                    break

            if statements_after_return:
                self.has_unreachable = True

            self.generic_visit(node)

    return_visitor = ReturnVisitor()
    return_visitor.visit(tree)
    if return_visitor.has_unreachable:
        correctness_issues.append("Detected potential unreachable code after return statements.")

    # Check for incorrect comparison with mutable defaults
    if re.search(r'def\s+\w+\s*\([^)]*=\s*\[\s*\][^)]*\)', code):
        correctness_issues.append("Mutable default argument (empty list) detected. This can cause unexpected behavior with shared state between calls.")

    # Check for incorrect string comparison
    if "is '" in code or "is \"" in code:
        correctness_issues.append("String comparison using 'is' instead of '=='. This can lead to unexpected behavior.")

    if not correctness_issues:
        correctness_issues.append("No obvious logical errors detected in static analysis.")

    return "\n".join(correctness_issues)


def analyze_scalability(code: str) -> str:
    """Identify scalability issues in the code."""
    tree = safe_parse(code)
    if not tree:
        return "Unable to parse code for scalability analysis."

    scalability_issues = check_scalability_issues(tree)

    # Additional checks

    # Check for caching
    if not re.search(r'@\s*cache|@\s*lru_cache|memoize|cache', code) and count_nested_loops(tree) > 0:
        scalability_issues.append("No caching mechanisms detected for potentially expensive operations.")

    # Check for bulk operations
    if re.search(r'for\s+\w+\s+in', code) and re.search(r'\.save\(\)|\.update\(\)|execute\(', code):
        scalability_issues.append("Potential N+1 query problem: database operations inside loops.")

    # Check for potential memory leaks
    if "append" in code and not "clear" in code and not "del" in code:
        scalability_issues.append("Growing collections detected without cleanup. Watch for potential memory growth.")

    # Check for thread safety for parallel processing
    if re.search(r'Thread|Process|concurrent|asyncio|threading', code) and not re.search(r'Lock|Semaphore|Queue|synchronized', code):
        scalability_issues.append("Concurrency detected without synchronization mechanisms.")

    # Pagination
    if re.search(r'all\(\)|\.all\(\)', code) and not re.search(r'limit|paginate|[:d+]', code):
        scalability_issues.append("Retrieving all records without pagination could cause issues with large datasets.")

    if not scalability_issues:
        scalability_issues.append("No obvious scalability issues detected in static analysis.")

    return "\n".join(scalability_issues)


def analyze_extensibility(code: str) -> str:
    """Analyze code extensibility and modularity."""
    tree = safe_parse(code)
    if not tree:
        return "Unable to parse code for extensibility analysis."

    extensibility_analysis = []

    # Analyze class structure and inheritance
    class_insights = find_class_structures(tree)
    extensibility_analysis.extend(class_insights)

    # Check for dependency injection patterns
    if re.search(r'__init__\s*\([^)]*\)', code):
        init_params = len(re.findall(r'self\.\w+\s*=\s*\w+', code))
        if init_params > 0:
            extensibility_analysis.append(f"Found {init_params} instance variables assigned in __init__, suggesting possible dependency injection.")

    # Check for interface/abstract classes
    if "ABC" in code or "abstractmethod" in code or "NotImplementedError" in code:
        extensibility_analysis.append("Abstract base classes or interfaces detected, which is good for extensibility.")

    # Check for function parameter counts (excessive params might need refactoring)
    function_params = re.findall(r'def\s+\w+\s*\(([^)]*)\)', code)
    long_param_lists = [p for p in function_params if len(p.split(',')) > 5]
    if long_param_lists:
        extensibility_analysis.append(f"Found {len(long_param_lists)} functions with more than 5 parameters. Consider refactoring with parameter objects.")

    # Check for design patterns
    if "Factory" in code:
        extensibility_analysis.append("Potential Factory pattern detected, good for extensibility.")
    if "Singleton" in code:
        extensibility_analysis.append("Potential Singleton pattern detected.")
    if "Observer" in code or "listener" in code.lower():
        extensibility_analysis.append("Potential Observer pattern detected, good for extensibility.")

    # Check for hard-coded values vs configuration
    magic_strings = len(re.findall(r'"[^"]+"', code)) + len(re.findall(r"'[^']+'", code))
    if magic_strings > 5:
        extensibility_analysis.append(f"Found {magic_strings} string literals. Consider moving to configuration for better extensibility.")

    if not extensibility_analysis:
        extensibility_analysis.append("No specific extensibility patterns detected in static analysis.")

    return "\n".join(extensibility_analysis)


def analyze_dependency(code: str) -> str:
    """Analyze dependencies and their management in the code."""
    dependency_analysis = []

    # Identify imports
    imports = find_potential_imports(code)

    if imports:
        dependency_analysis.append(f"Detected {len(imports)} imports: {', '.join(imports)}")

        # Check for version pinning
        if "==" in code and ("requirements" in code or "setup.py" in code):
            dependency_analysis.append("Version pinning detected in dependencies, which is good practice.")
        elif any(imp in code for imp in imports) and not "==" in code:
            dependency_analysis.append("No version pinning detected. Consider specifying version requirements.")

        # Common dependency risks
        risk_libs = {
            "requests": "Check for proper timeout handling and exception management",
            "sqlite3": "Local file database - ensure proper file permissions and query parameterization",
            "subprocess": "Potential command injection risk - validate inputs thoroughly",
            "flask": "Ensure DEBUG=False in production",
            "django": "Check for proper security settings in settings.py",
        }

        for lib in imports:
            if lib in risk_libs:
                dependency_analysis.append(f"Using {lib}: {risk_libs[lib]}")

        # Deprecated libraries warning
        deprecated = {
            "imp": "Deprecated since Python 3.4, use importlib instead",
            "urllib2": "Deprecated since Python 3, use urllib.request instead",
            "django.utils.six": "Deprecated, use the 'six' package directly"
        }

        for lib in imports:
            if lib in deprecated:
                dependency_analysis.append(f"Warning: {lib} is {deprecated[lib]}")
    else:
        dependency_analysis.append("No explicit imports or dependencies detected.")

    # Additional dependency practices
    if "requirements.txt" in code or "setup.py" in code or "Pipfile" in code:
        dependency_analysis.append("Dependency management files detected, which is good practice.")

    if not dependency_analysis:
        dependency_analysis.append("No dependency management information detected in static analysis.")

    return "\n".join(dependency_analysis)

# Register tool functions
register_tool("time_complexity", analyze_time_complexity)
register_tool("space_complexity", analyze_space_complexity)
register_tool("edge_cases", analyze_edge_cases)
register_tool("code_clarity", analyze_code_clarity)
register_tool("security", analyze_security)
register_tool("correctness", analyze_correctness)
register_tool("scalability", analyze_scalability)
register_tool("extensibility", analyze_extensibility)
register_tool("dependency", analyze_dependency)
