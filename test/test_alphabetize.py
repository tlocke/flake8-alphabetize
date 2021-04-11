from ast import parse

from flake8_alphabetize import Alphabetize
from flake8_alphabetize.core import AzImport, _find_errors, _find_imports

import pytest


def test_find_imports():
    pystr = """
if True:
    import scramp
"""
    assert _find_imports(parse(pystr)) == []


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

    az = AzImport([], imports[0])

    assert az.error == error


@pytest.mark.parametrize(
    "app_names,pystr_a,pystr_b,is_lt",
    [
        [[], "from pg8000.converters import BIGINT, BIGINT_ARRAY", "import pytz", True],
        [
            [],
            "from pg8000.native import Connection",
            "from ._version import get_versions",
            True,
        ],
        [
            [],
            "from ._version import get_versions",
            "from pg8000.native import Connection",
            False,
        ],
        [
            [],
            "import uuid",
            "import scramp",
            True,
        ],
        [
            [],
            "import time",
            "from collections import OrderedDict",
            True,
        ],
        [
            [],
            "import pg8000.dbapi",
            "from pg8000.converters import pg_interval_in",
            True,
        ],
        [
            [],
            "from __future__ import print_function",
            "import decimal",
            True,
        ],
        [
            [],
            "from pg8000.converters import ARRAY",
            "from pg8000.converters import BIGINT",
            False,
        ],
        [
            [],
            "from pg8000.converters import BIGINT",
            "from pg8000.converters import ARRAY",
            False,
        ],
        [
            ["pg8000"],
            "import scramp",
            "import pg8000",
            True,
        ],
    ],
)
def test_AzImport_lt(app_names, pystr_a, pystr_b, is_lt):
    imports_a = _find_imports(parse(pystr_a))
    assert len(imports_a) == 1
    az_a = AzImport(app_names, imports_a[0])

    imports_b = _find_imports(parse(pystr_b))
    assert len(imports_b) == 1
    az_b = AzImport(app_names, imports_b[0])

    assert (az_a < az_b) == is_lt


def test_AzImport_str():
    pystr = "from .version import version"
    node = parse(pystr)
    imports = _find_imports(node)

    az = AzImport([], imports[0])

    assert str(az) == pystr


@pytest.mark.parametrize(
    "app_names,pystr,errors",
    [
        [[], "", []],
        [
            [],
            """import decimal
import os""",
            [],
        ],
        [
            [],
            """import versioneer
from os import path""",
            [
                (
                    2,
                    0,
                    "AZ100 Import statements are in the wrong order. "
                    "'from os import path' should be before 'import versioneer'",
                    Alphabetize,
                ),
            ],
        ],
        [
            [],
            "from datetime import timedelta, date",
            [
                (
                    1,
                    0,
                    "AZ200 Imported names are in the wrong order. Should be date, "
                    "timedelta",
                    Alphabetize,
                )
            ],
        ],
        [
            [],
            """from pg8000 import BIGINT
from pg8000 import ARRAY""",
            [
                (
                    2,
                    0,
                    "AZ300 Import statements should be combined. 'from pg8000 import "
                    "BIGINT' should be combined with 'from pg8000 import ARRAY'",
                    Alphabetize,
                )
            ],
        ],
        [
            ["pg8000"],
            """import scramp
from pg8000 import ARRAY""",
            [],
        ],
        [
            ["pg8000"],
            """from pg8000 import ARRAY
import scramp""",
            [
                (
                    2,
                    0,
                    "AZ100 Import statements are in the wrong order. 'import scramp' "
                    "should be before 'from pg8000 import ARRAY'",
                    Alphabetize,
                )
            ],
        ],
        [
            [],
            """import socket
import sys
import struct
""",
            [
                (
                    3,
                    0,
                    "AZ100 Import statements are in the wrong order. 'import struct' "
                    "should be before 'import sys'",
                    Alphabetize,
                )
            ],
        ],
        [
            ["scramp"],
            """import scramp
from ._version import vers
""",
            [],
        ],
    ],
)
def test_find_errors(app_names, pystr, errors):
    tree = parse(pystr)

    actual_errors = _find_errors(app_names, tree)

    assert actual_errors == errors
