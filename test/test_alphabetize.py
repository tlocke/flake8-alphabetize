from ast import parse

from alphabetize.core import _find_errors, AzImport, _find_imports
from alphabetize import Alphabetize

import pytest


@pytest.mark.parametrize(
    "pystr,errors",
    [
        ["", []],
        [
            """import decimal
import os""",
            [],
        ],
        [
            """import versioneer
from os import path""",
            [
                (
                    2,
                    0,
                    "AZ000 Import statements are in the wrong order. "
                    "'from os import path' should be before 'import versioneer'",
                    Alphabetize,
                )
            ],
        ],
    ],
)
def test_find_errors(pystr, errors):
    tree = parse(pystr)

    actual_errors = _find_errors(tree)

    assert actual_errors == errors


@pytest.mark.parametrize(
    "pystr_a,pystr_b",
    [
        ["from pg8000.converters import BIGINT, BIGINT_ARRAY", "import pytz"],
    ],
)
def test_AzImport_lt(pystr_a, pystr_b):
    imports_a = _find_imports(parse(pystr_a))
    assert len(imports_a) == 1
    az_a = AzImport(imports_a[0])

    imports_b = _find_imports(parse(pystr_b))
    assert len(imports_b) == 1
    az_b = AzImport(imports_b[0])

    assert az_a < az_b


@pytest.mark.parametrize(
    "pystr,error",
    [
        [
            "from pg8000.converters import BIGINT_ARRAY, BIGINT",
            (
                1,
                0,
                "AZ200 Imported names are in the wrong order. Should be BIGINT, "
                "BIGINT_ARRAY",
                Alphabetize,
            ),
        ],
    ],
)
def test_AzImport_init(pystr, error):
    node = parse(pystr)
    imports = _find_imports(node)

    az = AzImport(imports[0])

    assert az.error == error
