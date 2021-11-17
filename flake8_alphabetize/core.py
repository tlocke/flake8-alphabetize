import sys
from ast import Assign, Constant, Import, ImportFrom, List, Module, Name, Str, Tuple
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
            "--application-names",
            type="string",
            metavar="APPLICATION_NAMES",
            default="",
            parse_from_config=True,
            help="Comma-separated list of package names. If an import is for a "
            "package in this list, it'll be in the application group of imports. "
            "Eg. 'myapp'.",
        )

    @classmethod
    def parse_options(cls, options):
        names = options.application_names
        cls.app_names = [] if (names is None or names == "") else names.split(",")


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


def _is_in_stdlib(name):
    if hasattr(sys, "stdlib_module_names"):
        return name in sys.stdlib_module_names
    else:
        return in_stdlib(name)


@total_ordering
class AzImport:
    def __init__(self, app_names, ast_node):
        self.node = ast_node
        self.error = None
        level = None
        group = None

        if isinstance(ast_node, Import):
            self.node_type = NodeTypeEnum.IMPORT
            names = ast_node.names

            self.module_name = names[0].name
            level = 0

        elif isinstance(ast_node, ImportFrom):
            module = ast_node.module
            self.module_name = "" if module is None else module
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
        elif _is_in_stdlib(self.module_name):
            group = GroupEnum.STDLIB
        elif level > 0:
            group = GroupEnum.APPLICATION
        else:
            group = GroupEnum.THIRD_PARTY
            for name in app_names:
                if name == self.module_name or self.module_name.startswith(f"{name}."):
                    group = GroupEnum.APPLICATION
                    break

        if group == GroupEnum.STDLIB:
            self.sorter = group, self.node_type, self.module_name
        else:
            m = self.module_name
            dot_idx = m.find(".")
            top_name = m if dot_idx == -1 else m[:dot_idx]
            self.sorter = group, level, top_name, self.node_type, m

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
            return f"from {level_str}{self.module_name} import {', '.join(names)}"
        else:
            raise AlphabetizeException(
                f"The node type {self.node_type} is not recognized."
            )


IMPORT_TYPES = Import, ImportFrom


def _find_nodes(tree):
    import_nodes = []
    list_node = None

    if isinstance(tree, Module):
        body = tree.body

        for n in body:

            if isinstance(n, IMPORT_TYPES):
                import_nodes.append(n)

            elif isinstance(n, Assign):

                for t in n.targets:

                    if isinstance(t, Name) and t.id == "__all__":
                        value = n.value

                        if isinstance(value, (List, Tuple)):
                            list_node = value

    return import_nodes, list_node


def _find_dunder_all_error(node):
    if node is not None:
        actual_list = []
        for el in node.elts:
            if isinstance(el, Constant):
                actual_list.append(el.value)
            elif isinstance(el, Str):
                actual_list.append(el.s)
            else:
                # Can't handle anything that isn't a string literal
                return

        expected_list = sorted(actual_list)
        if expected_list != actual_list:
            return _make_error(
                node,
                "400",
                f"The names in the __all__ are in the wrong order. The order should "
                f"be {', '.join(expected_list)}",
            )


def _find_errors(app_names, tree):
    import_nodes, list_node = _find_nodes(tree)
    errors = []

    dunder_all_error = _find_dunder_all_error(list_node)
    if dunder_all_error is not None:
        errors.append(dunder_all_error)

    imports = []
    for imp in import_nodes:
        if isinstance(imp, Import) and len(imp.names) > 1:
            return errors
        else:
            imports.append(AzImport(app_names, imp))

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

        p = n

    return errors
