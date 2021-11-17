from flake8_alphabetize.core import Alphabetize

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

Alphabetize.version = __version__

__all__ = ["Alphabetize", "__version__"]
