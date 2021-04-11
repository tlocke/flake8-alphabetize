import ast
from enum import IntEnum
from functools import total_ordering

from stdlib_list import in_stdlib


class AlphabetizeException(Exception):
    pass


class Alphabetize:
    name = "alphabetize"

    def __init__(self, tree):
        self.tree = tree

    def __iter__(self):
        errors = _find_errors(Alphabetize.app_names, self.tree)
        return iter(errors)

    @staticmethod
    def add_options(option_manager):
        option_manager.add_option(
            "--application-package-names",
            type="string",
            metavar="IMPORT_NAMES",
            default="",
            parse_from_config=True,
            help="Comma-separated list of package names. If an import is for a "
            "package in this list, it'll be in the application group of imports. "
            "Eg. 'myapp'.",
        )

    @classmethod
    def parse_options(cls, options):
        cls.app_names = options.application_package_names


def _make_error(node, code, message):
    return (node.lineno, node.col_offset, f"AZ{code} {message}", Alphabetize)


class GroupEnum(IntEnum):
    FUTURE = 1
    STDLIB = 2
    THIRD_PARTY = 3
    APPLICATION = 4


class NodeTypeEnum(IntEnum):
    IMPORT = 1
    IMPORT_FROM = 2


@total_ordering
class AzImport:
    def __init__(self, app_names, ast_node):
        self.node = ast_node
        self.error = None
        level = None
        group = None

        if isinstance(ast_node, ast.Import):
            self.node_type = NodeTypeEnum.IMPORT
            names = ast_node.names
            if len(names) != 1:
                return

            self.module_name = names[0].name
            level = 0

        elif isinstance(ast_node, ast.ImportFrom):
            self.module_name = ast_node.module
            self.node_type = NodeTypeEnum.IMPORT_FROM

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
            level = ast_node.level

        else:
            raise AlphabetizeException(f"Node type {type(ast_node)} not recognized")

        if self.module_name == "__future__":
            group = GroupEnum.FUTURE
        elif in_stdlib(self.module_name):
            group = GroupEnum.STDLIB
        elif level > 0:
            group = GroupEnum.APPLICATION
        else:
            for name in app_names:
                if name == self.module_name or self.module_name.startswith(f"{name}."):
                    group = GroupEnum.APPLICATION
                    break
            group = GroupEnum.THIRD_PARTY

        if group == GroupEnum.STDLIB:
            self.sorter = group, self.node_type, self.module_name
        else:
            m = self.module_name
            first_dot = m.find(".")
            top_name = m if first_dot == -1 else m[:first_dot]
            self.sorter = group, top_name, self.node_type, m

    def __eq__(self, other):
        return self.sorter == other.sorter

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


def _find_errors(app_names, tree):
    imports = [AzImport(app_names, imp) for imp in _find_imports(tree)]
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

        if n == p:
            errors.append(
                _make_error(
                    n.node,
                    "300",
                    f"Import statements should be combined. '{p}' should be "
                    f"combined with '{n}'",
                )
            )
        elif n < p:
            errors.append(
                _make_error(
                    n.node,
                    "100",
                    f"Import statements are in the wrong order. '{n}' should be "
                    f"before '{p}'",
                )
            )
    return errors
