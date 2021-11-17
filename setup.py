import setuptools

import versioneer


long_description = """
A Flake8 style checker for alphabetizing import and \\_\\_all\\_\\_. Please see [the
documentation](https://github.com/tlocke/flake8-alphabetize)
"""

setuptools.setup(
    name="flake8-alphabetize",
    license="Unlicense",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="A Python style checker for alphabetizing import and __all__.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tony Locke",
    author_email="tlocke@tlocke.org.uk",
    url="https://github.com/tlocke/flake8-alphabetize",
    packages=[
        "flake8_alphabetize",
    ],
    install_requires=[
        "flake8 > 3.0.0",
        "stdlib_list == 0.8.0",
    ],
    entry_points={
        "flake8.extension": [
            "AZ = flake8_alphabetize:Alphabetize",
        ],
    },
    classifiers=[
        "Framework :: Flake8",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
