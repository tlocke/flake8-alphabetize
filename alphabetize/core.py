import ast


class Alphabetize:
    name = "alphabetize"

    def __init__(self, tree):
        self.errors = _find_errors(tree)

    def __iter__(self):
        return iter(self.errors)


class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imp_nodes = []

    def visit_Import(self, imp_node):
        self.imp_nodes.append(imp_node)

    def visit_ImportFrom(self, imp_node):
        self.imp_nodes.append(imp_node)


def _find_errors(tree):
    visitor = ImportVisitor()
    visitor.visit(tree)
    imp_nodes = visitor.imp_nodes
    errors = []

    if len(imp_nodes) < 2:
        return errors

    p = imp_nodes[0]
    for n in imp_nodes[1:]:
        if n.module < p.module:
            errors.append(
                (
                    n.lineno,
                    n.col_offset,
                    f"AZ000 Import statements are in the wrong order. 'from "
                    f"{_imp_from_to_str(n)}' should be before '{_imp_from_to_str(p)}'",
                    Alphabetize,
                )
            )
        p = n
    return errors


def _imp_from_to_str(node):
    names_str = ", ".join(
        n.name + ("" if n.asname is None else f" as {n.asname}") for n in node.names
    )
    return f"from {node.module} import {names_str}"
