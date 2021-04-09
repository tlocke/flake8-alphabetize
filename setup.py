import setuptools

import versioneer

from os import path


long_description = """A Flake8 style checker for alphabetizing import and __all__.",
Please see the [documentation](https://github.com/tlocke/flake8-alphabetize)"""

setuptools.setup(
    name="flake8_alphabetize",
    license="Unlicense",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="A Python style checker for alphabetizing import and __all__.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tony Locke",
    author_email="tlocke@tlocke.org.uk",
    url="https://github.com/tlocke/flake8_alphabetize",
    packages=[
        "alphabetize",
    ],
    install_requires=[
        "flake8 > 3.0.0",
        "stdlib_list == 0.8.0",
    ],
    entry_points={
        "flake8.extension": [
            "ALP = alphabetize:Alphabetize",
        ],
    },
    classifiers=[
        "Framework :: Flake8",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
)