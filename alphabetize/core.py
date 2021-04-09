import ast
from functools import total_ordering

from stdlib_list import in_stdlib


class AlphabetizeException(Exception):
    pass


class Alphabetize:
    name = "alphabetize"

    def __init__(self, tree):
        self.errors = _find_errors(tree)

    def __iter__(self):
        return iter(self.errors)


def _make_error(node, code, message):
    return (node.lineno, node.col_offset, f"AZ{code} {message}", Alphabetize)


@total_ordering
class AzImport:
    def __init__(self, ast_node):
        self.node = ast_node
        self.error = None

        if isinstance(ast_node, ast.Import):
            self.is_import = True
            names = ast_node.names
            if len(names) != 1:
                self.error = "pep8"
                return

            self.module_name = names[0].name

        elif isinstance(ast_node, ast.ImportFrom):
            self.is_import = False
            self.module_name = ast_node.module
            ast_names = ast_node.names
            names = [n.name for n in ast_names]
            expected_names = sorted(names)
            if names != expected_names:
                self.error = _make_error(
                    self.node,
                    200,
                    f"Imported names are in the wrong order. Should be "
                    f"{', '.join(expected_names)}",
                )

        else:
            raise AlphabetizeException(f"Node type {type(ast_node)} not recognized")

        self.in_stdlib = in_stdlib(self.module_name)

    def __eq__(self, other):
        return self.node == other.node

    def __lt__(self, other):
        return self.module_name < other.module_name

    def __str__(self):
        if self.is_import:
            return f"import {self.module_name}"
        else:
            names = [
                n.name + ("" if n.asname is None else f" as {n.asname}")
                for n in self.node.names
            ]
            return f"from {self.node.module} import {', '.join(names)}"


def _find_imports(tree):
    return [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]


def _find_errors(tree):
    imports = [AzImport(imp) for imp in _find_imports(tree)]
    errors = []

    if len(imports) < 2:
        return errors

    p = imports[0]
    for n in imports[1:]:
        if n < p:
            errors.append(
                _make_error(
                    n.node,
                    "000",
                    f"Import statements are in the wrong order. '{n}' should be "
                    f"before '{p}'",
                )
            )
        p = n
    return errors
