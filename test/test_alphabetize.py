from ast import parse

from alphabetize.core import _find_errors

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
            [],
        ],
    ],
)
def test_find_errors(pystr, errors):
    tree = parse(pystr)

    actual_errors = _find_errors(tree)

    assert actual_errors == errors
