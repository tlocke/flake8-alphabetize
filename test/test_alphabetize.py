from ast import List, Tuple, parse

from flake8_alphabetize import Alphabetize
from flake8_alphabetize.core import (
    AzImport,
    _find_dunder_all_error,
    _find_errors,
    _find_nodes,
)

import pytest


@pytest.mark.parametrize(
    "pystr,import_node_types,expected_type",
    [
        [
            """
if True:
    import scramp
""",
            [],
            None,
        ],
        [
            "__all__ = []",
            [],
            List,
        ],
        [
            "__all__ = ()",
            [],
            Tuple,
        ],
    ],
)
def test_find_nodes(pystr, import_node_types, expected_type):
    import_nodes, list_node = _find_nodes(parse(pystr))

    assert [type(n) for n in import_nodes] == import_node_types

    if expected_type is None:
        assert list_node is None
    else:
        assert type(list_node) == expected_type


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
        [
            "from . import logging",
            None,
        ],
    ],
)
def test_AzImport_init(pystr, error):
    node = parse(pystr)
    az = AzImport([], node.body[0])

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
        [
            [],
            "from . import scramp",
            "from .version import ver",
            True,
        ],
    ],
)
def test_AzImport_lt(app_names, pystr_a, pystr_b, is_lt):
    node_a = parse(pystr_a)
    az_a = AzImport(app_names, node_a.body[0])

    node_b = parse(pystr_b)
    az_b = AzImport(app_names, node_b.body[0])

    assert (az_a < az_b) == is_lt


@pytest.mark.parametrize(
    "pystr",
    [
        "from .version import version",
        "from . import version",
    ],
)
def test_AzImport_str(pystr):
    node = parse(pystr)

    az = AzImport([], node.body[0])

    assert str(az) == pystr


@pytest.mark.parametrize(
    "pystr",
    [
        "[]",
        "()",
        "[ScramServer]",
        "('ScramClient',)",
        "['ScramClient', 'ScramServer']",
        "('ScramClient', 'ScramServer')",
    ],
)
def test_find_dunder_all_ok(pystr):
    node = parse(pystr)
    sequence_node = node.body[-1].value

    assert _find_dunder_all_error(sequence_node) is None


@pytest.mark.parametrize(
    "pystr,error",
    [
        [
            "['ScramServer', 'ScramClient']",
            "AZ400 The names in the __all__ are in the wrong order. The order should "
            "be ScramClient, ScramServer",
        ],
        [
            "('ScramServer', 'ScramClient')",
            "AZ400 The names in the __all__ are in the wrong order. The order should "
            "be ScramClient, ScramServer",
        ],
    ],
)
def test_find_dunder_all_error(pystr, error, py_version):
    node = parse(pystr)
    sequence_node = node.body[-1].value
    if isinstance(sequence_node, Tuple):
        col_offset = 1 if py_version < (3, 8) else 0
    else:
        col_offset = 0
    expected = (1, col_offset, error, Alphabetize)

    assert _find_dunder_all_error(sequence_node) == expected


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
        [  # We can't check __all__ if the elements aren't literal strings
            [],
            """from scramp.core import ScramClient, ScramServer
__all__ = [ScramServer, ScramClient]
""",
            [],
        ],
        [  # Wait for Flake8 fixes to be made first
            [],
            """import time
import datetime, scramp""",
            [],
        ],
    ],
)
def test_find_errors(app_names, pystr, errors):
    tree = parse(pystr)

    actual_errors = _find_errors(app_names, tree)

    assert actual_errors == errors
