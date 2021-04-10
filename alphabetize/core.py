import ast
from enum import IntEnum
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


class GroupEnum(IntEnum):
    STDLIB = 1
    THIRD_PARTY = 2
    APPLICATION = 3


class NodeTypeEnum(IntEnum):
    IMPORT = 1
    IMPORT_FROM = 2


@total_ordering
class AzImport:
    def __init__(self, ast_node):
        self.node = ast_node
        self.error = None
        self.level = None

        if isinstance(ast_node, ast.Import):
            self.node_type = NodeTypeEnum.IMPORT
            names = ast_node.names
            if len(names) != 1:
                return

            self.module_name = names[0].name
            self.level = 0

        elif isinstance(ast_node, ast.ImportFrom):
            self.node_type = NodeTypeEnum.IMPORT_FROM
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
            self.level = ast_node.level

        else:
            raise AlphabetizeException(f"Node type {type(ast_node)} not recognized")

        if in_stdlib(self.module_name):
            self.group = GroupEnum.STDLIB
        elif self.level > 0:
            self.group = GroupEnum.APPLICATION
        else:
            self.group = GroupEnum.THIRD_PARTY

        if self.group == GroupEnum.STDLIB:
            self.sorter = self.group, self.node_type, self.module_name
        else:
            m = self.module_name
            first_dot = m.find(".")
            top_name = m if first_dot == -1 else m[:first_dot]
            self.sorter = self.group, top_name, self.node_type, m

    def __eq__(self, other):
        return self.node == other.node

    def __lt__(self, other):
        return self.sorter < other.sorter

    def __str__(self):
        if self.node_type == NodeTypeEnum.IMPORT:
            return f"import {self.module_name}"
        elif self.node_type == NodeTypeEnum.IMPORT_FROM:
            level = self.node.level
            level_str = "" if level == 0 else "." * level
            names = [
                n.name + ("" if n.asname is None else f" as {n.asname}")
                for n in self.node.names
            ]
            return f"from {level_str}{self.node.module} import {', '.join(names)}"
        else:
            raise AlphabetizeException(
                f"The node type {self.node_type} is not recognized."
            )


IMPORT_TYPES = ast.Import, ast.ImportFrom


def _find_imports(tree):
    if isinstance(tree, ast.Module):
        body = tree.body
        if isinstance(body, IMPORT_TYPES):
            return [body]
        elif isinstance(body, list):
            return [n for n in body if isinstance(n, IMPORT_TYPES)]
        else:
            return []


def _find_errors(tree):
    imports = [AzImport(imp) for imp in _find_imports(tree)]
    errors = []

    len_imports = len(imports)
    if len_imports == 0:
        return errors

    p = imports[0]
    if p.error is not None:
        errors.append(p.error)

    if len_imports < 2:
        return errors

    for n in imports[1:]:

        if n.error is not None:
            errors.append(n.error)

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
