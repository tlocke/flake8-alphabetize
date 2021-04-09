import ast
from functools import total_ordering
from stdlib_list import in_stdlib


class Alphabetize:
    name = "alphabetize"

    def __init__(self, tree):
        self.errors = _find_errors(tree)

    def __iter__(self):
        return iter(self.errors)


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

        self.in_stdlib = in_stdlib(self.module_name)

    def __eq__(self, other):
        return self.node == other.node

    def __lt__(self, other):
        self.module_name < other.module_name

    def __str__(self):
        if self.is_import:
            return f"import {self.module_name}"
        else:
            names = [
                n.name + ("" if n.asname is None else f" as {n.asname}")
                for n in node.names
            ]
            return f"from {node.module} import {', '.join(names)}"


class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = []

    def visit_Import(self, node):
        self.imports.append(AzImport(node))

    def visit_ImportFrom(self, node):
        self.imports.append(AzImport(node))


def _find_errors(tree):
    visitor = ImportVisitor()
    visitor.visit(tree)
    imports = visitor.imports
    errors = []

    if len(imports) < 2:
        return errors

    p = imports[0]
    for n in imports[1:]:
        if n < p:
            errors.append(
                (
                    n.lineno,
                    n.col_offset,
                    f"AZ000 Import statements are in the wrong order. '{p}' should "
                    f"be before '{n}'",
                    Alphabetize,
                )
            )
        p = n
    return errors
