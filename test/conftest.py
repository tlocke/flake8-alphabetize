import sys

import pytest


@pytest.fixture(scope="module")
def py_version():
    version = sys.version_info
    return version.major, version.minor
