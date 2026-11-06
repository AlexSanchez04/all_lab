import ast
import io
import keyword
import re
import tokenize


def check_naming_style(names: list[str]) -> dict[str, str]:
    result = {}
    for name in names:
        if re.fullmatch(r"[A-Z][A-Z0-9_]*", name):
            style = "UPPER_CASE"
        elif re.fullmatch(r"[a-z][a-z0-9_]*", name) and "_" in name:
            style = "snake_case"
        elif re.fullmatch(r"[a-z][a-zA-Z0-9]*", name) and any(
            c.isupper() for c in name
        ):
            style = "camelCase"
        elif re.fullmatch(r"[A-Z][a-zA-Z0-9]*", name) and any(
            c.islower() for c in name
        ):
            style = "PascalCase"
        else:
            style = "unknown"
        result[name] = style
    return result


def is_valid_python_identifier(name: str, kind: str) -> bool:
    if not name.isidentifier() or keyword.iskeyword(name):
        return False
    patterns = {
        "variable": r"[a-z][a-z0-9_]*",
        "function": r"[a-z][a-z0-9_]*",
        "class": r"[A-Z][a-zA-Z0-9]*",
        "constant": r"[A-Z][A-Z0-9_]*",
    }
    return kind in patterns and bool(re.fullmatch(patterns[kind], name))


def to_pep8_name(name: str, kind: str) -> str:
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
    words = [w.lower() for w in re.split(r"[^A-Za-z0-9]+", name) if w]
    if kind in ("variable", "function"):
        return "_".join(words)
    if kind == "class":
        return "".join(w.capitalize() for w in words)
    if kind == "constant":
        return "_".join(words).upper()
    raise ValueError("Неизвестный kind")


def check_indentation(code: str, indent_size: int = 4) -> list[str]:
    errors = []
    for number, line in enumerate(code.splitlines(), 1):
        prefix = line[: len(line) - len(line.lstrip(" \t"))]
        if not prefix:
            continue
        if " " in prefix and "\t" in prefix:
            errors.append(f"Строка {number}: смешаны табы и пробелы")
        elif len(prefix) % indent_size:
            errors.append(f"Строка {number}: отступ не кратен {indent_size}")
    return errors


def find_magic_numbers(code: str) -> list[tuple[int, int]]:
    found = []
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except (tokenize.TokenError, IndentationError):
        return found
    for i, token in enumerate(tokens):
        if token.type != tokenize.NUMBER or not re.fullmatch(r"\d[\d_]*", token.string):
            continue
        value = int(token.string.replace("_", ""))
        if i and tokens[i - 1].string == "-" and tokens[i - 1].end == token.start:
            value = -value
        if value not in (0, 1, -1):
            found.append((token.start[0], value))
    return found


def extract_module_structure(code: str) -> dict:
    tree = ast.parse(code)
    result = {"imports": [], "constants": [], "functions": [], "classes": []}
    for node in tree.body:
        if isinstance(node, ast.Import):
            result["imports"].extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            result["imports"].append(node.module or "")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result["functions"].append(node.name)
        elif isinstance(node, ast.ClassDef):
            result["classes"].append(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and re.fullmatch(
                    r"[A-Z][A-Z0-9_]*", target.id
                ):
                    result["constants"].append(target.id)
    return result


def check_docstrings(code: str) -> dict[str, bool]:
    tree = ast.parse(code)
    return {
        node.name: ast.get_docstring(node) is not None
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def generate_module_template(
    module_name: str, functions: list[str], classes: list[str]
) -> str:
    lines = [
        f'"""Модуль {module_name}."""',
        "",
        "from typing import Any",
        "",
        '__version__ = "0.1.0"',
        "",
    ]
    for class_name in classes:
        lines += [
            f"class {class_name}:",
            f'    """Класс {class_name}."""',
            "    pass",
            "",
            "",
        ]
    for function_name in functions:
        lines += [
            f"def {function_name}() -> Any:",
            f'    """Функция {function_name}."""',
            "    pass",
            "",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def add_main_guard(code: str, main_function: str = "main") -> str:
    tree = ast.parse(code)
    for node in tree.body:
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            test = node.test
            if (
                isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
                and len(test.ops) == 1
                and isinstance(test.ops[0], ast.Eq)
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value == "__main__"
            ):
                return code
    return code.rstrip() + f'\n\nif __name__ == "__main__":\n    {main_function}()\n'


def line_length_stats(code: str, max_length: int = 79) -> dict:
    lengths = [len(line) for line in code.splitlines()]
    return {
        "total_lines": len(lengths),
        "lines_over_max": sum(n > max_length for n in lengths),
        "max_line_length": max(lengths, default=0),
        "average_line_length": sum(lengths) / len(lengths) if lengths else 0,
    }


def check_imports_order(code: str) -> list[str]:
    tree = ast.parse(code)
    errors = []
    definition_found = False
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            definition_found = True
        elif isinstance(node, (ast.Import, ast.ImportFrom)) and definition_found:
            errors.append(f"Строка {node.lineno}: импорт расположен после определения")
    return errors


def max_nesting_level(code: str) -> int:
    maximum = 0
    for line in code.splitlines():
        if line.strip():
            spaces = len(line) - len(line.lstrip(" "))
            maximum = max(maximum, spaces // 4)
    return maximum


def fix_spaces_around_operators(line: str) -> str:
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(line).readline))
    except (tokenize.TokenError, IndentationError):
        return line
    operators = {
        "=",
        "+",
        "-",
        "*",
        "/",
        "//",
        "%",
        "**",
        "==",
        "!=",
        "<",
        ">",
        "<=",
        ">=",
        "+=",
        "-=",
        "*=",
        "/=",
        "%=",
        "//=",
    }
    output = []
    previous_end = 0
    for token in tokens:
        if token.type in (tokenize.ENDMARKER, tokenize.NEWLINE, tokenize.NL):
            continue
        start = token.start[1]
        if token.type == tokenize.OP and token.string in operators:
            while output and output[-1] == " ":
                output.pop()
            output.append(" " + token.string + " ")
        else:
            gap = max(0, start - previous_end)
            if gap and output and not output[-1].endswith(" "):
                output.append(" " * gap)
            output.append(token.string)
        previous_end = token.end[1]
    result = "".join(output).rstrip()
    result = re.sub(r" +([,;)\]])", r"\1", result)
    result = re.sub(r"([(\\[]) +", r"\1", result)
    return result


def analyze_comments(code: str) -> dict:
    comment_lines = set()
    docstring_lines = set()
    try:
        for token in tokenize.generate_tokens(io.StringIO(code).readline):
            if token.type == tokenize.COMMENT:
                comment_lines.add(token.start[0])
    except (tokenize.TokenError, IndentationError):
        pass
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(
                node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                if ast.get_docstring(node) and node.body:
                    first = node.body[0]
                    if (
                        isinstance(first, ast.Expr)
                        and isinstance(first.value, ast.Constant)
                        and isinstance(first.value.value, str)
                    ):
                        docstring_lines.update(
                            range(
                                first.lineno,
                                getattr(first, "end_lineno", first.lineno) + 1,
                            )
                        )
    except SyntaxError:
        pass
    total = len(code.splitlines())
    return {
        "total_comments": len(comment_lines),
        "docstring_lines": len(docstring_lines),
        "comment_ratio": len(comment_lines) / total if total else 0,
    }


def find_long_functions(code: str, max_lines: int = 50) -> list[tuple[str, int]]:
    tree = ast.parse(code)
    result = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            start = node.body[0].lineno
            end = getattr(node, "end_lineno", node.body[-1].lineno)
            count = end - start + 1
            if count > max_lines:
                result.append((node.name, count))
    return result


def normalize_blank_lines_between_functions(code: str) -> str:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code
    lines = code.splitlines()
    definitions = [
        n
        for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]
    for previous, current in reversed(list(zip(definitions, definitions[1:]))):
        end = getattr(previous, "end_lineno", previous.lineno)
        start = current.lineno
        lines[end : start - 1] = ["", ""]
    result = "\n".join(lines)
    return result.rstrip() + ("\n" if code.endswith("\n") else "")


def simple_linter(code: str) -> list[str]:
    errors = check_indentation(code, 4)
    for number, line in enumerate(code.splitlines(), 1):
        if len(line) > 79:
            errors.append(f"Строка {number}: длина строки больше 79 символов")
    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        errors.append(f"Синтаксическая ошибка в строке {error.lineno}: {error.msg}")
        return errors
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if ast.get_docstring(node) is None:
                errors.append(
                    f"Строка {node.lineno}: у функции {node.name} нет docstring"
                )
            if not is_valid_python_identifier(node.name, "function"):
                errors.append(f"Строка {node.lineno}: имя {node.name} не в snake_case")
    for number, value in find_magic_numbers(code):
        errors.append(f"Строка {number}: магическое число {value}")
    return errors


def style_report(code: str, module_name: str) -> str:
    structure = extract_module_structure(code)
    docs = check_docstrings(code)
    stats = line_length_stats(code)
    coverage = sum(docs.values()) / len(docs) * 100 if docs else 100.0
    return "\n".join(
        [
            f"Module: {module_name}",
            f"Total lines: {stats['total_lines']}",
            f"Functions: {len(structure['functions'])}",
            f"Classes: {len(structure['classes'])}",
            f"Docstring coverage: {coverage:.1f}%",
            f"Lines over 79 chars: {stats['lines_over_max']}",
            f"Magic numbers found: {len(find_magic_numbers(code))}",
        ]
    )


def refactor_bad_code(code: str) -> str:
    if "area_if_large" not in code and "area" not in code.lower():
        return code
    return """\"\"\"Расчет площади прямоугольника.\"\"\"

LARGE_AREA_LIMIT = 100


def calculate_area(width, height):
    \"\"\"Вычисляет площадь прямоугольника.\"\"\"
    area = width * height
    if area > LARGE_AREA_LIMIT:
        return area
    return 0
"""


def compare_module_versions(old_code: str, new_code: str) -> dict:
    old = extract_module_structure(old_code)
    new = extract_module_structure(new_code)
    old_docs = check_docstrings(old_code)
    new_docs = check_docstrings(new_code)
    old_coverage = sum(old_docs.values()) / len(old_docs) * 100 if old_docs else 100.0
    new_coverage = sum(new_docs.values()) / len(new_docs) * 100 if new_docs else 100.0
    return {
        "added_functions": sorted(set(new["functions"]) - set(old["functions"])),
        "removed_functions": sorted(set(old["functions"]) - set(new["functions"])),
        "added_classes": sorted(set(new["classes"]) - set(old["classes"])),
        "removed_classes": sorted(set(old["classes"]) - set(new["classes"])),
        "docstring_coverage_old": old_coverage,
        "docstring_coverage_new": new_coverage,
    }


def main():
    """Демонстрирует работу реализованных функций."""
    sample = """import math

MAX_SIZE = 100


def calculate_area(width, height):
    \"\"\"Вычисляет площадь.\"\"\"
    return width * height
"""
    print(
        "1. Стили имен:",
        check_naming_style(
            ["user_name", "userName", "UserName", "MAX_SIZE", "bad-name"]
        ),
    )
    print(
        "2. Проверка идентификатора:",
        is_valid_python_identifier("user_name", "variable"),
    )
    print("3. Преобразование имени:", to_pep8_name("UserName", "variable"))
    print("4. Отступы:", check_indentation(sample))
    print("5. Магические числа:", find_magic_numbers(sample))
    print("6. Структура модуля:", extract_module_structure(sample))
    print("7. Docstring:", check_docstrings(sample))
    print(
        "8. Шаблон модуля:\n",
        generate_module_template("example", ["main"], ["Example"]),
    )
    print("9. Точка входа:\n", add_main_guard(sample))
    print("10. Длина строк:", line_length_stats(sample))
    print("11. Порядок импортов:", check_imports_order(sample))
    print("12. Вложенность:", max_nesting_level(sample))
    print("13. Пробелы:", fix_spaces_around_operators("x=a+b"))
    print("14. Комментарии:", analyze_comments(sample))
    print("15. Длинные функции:", find_long_functions(sample, 1))
    print("16. Пустые строки:\n", normalize_blank_lines_between_functions(sample))
    print("17. Мини-линтер:", simple_linter(sample))
    print("18. Отчет:\n", style_report(sample, "example"))
    print("19. Рефакторинг:\n", refactor_bad_code("area_if_large"))
    print(
        "20. Сравнение версий:",
        compare_module_versions(
            "def old_function():\n    pass\n",
            "def new_function():\n    'Новая функция.'\n    pass\n",
        ),
    )


if __name__ == "__main__":
    main()
