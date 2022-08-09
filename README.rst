==================
Flake8 Alphabetize
==================

Alphabetize is a `Flake8 <https://flake8.pycqa.org/en/latest/>`_ plugin for checking the
order of ``import`` statements and the ``__all__`` list. It is designed to work well
with the `Black <https://black.readthedocs.io/en/stable/index.html>`_ formatting tool,
in that Black never alters the
`Abstract Syntax Tree <https://en.wikipedia.org/wiki/Abstract_syntax_tree>`_ (AST),
while Alphabetize is *only* interested in the AST, and so the two tools never conflict.
In the spirit of Black, Alphabetize is an 'uncompromising import style checker' in that
the style can't be configured, there's just one style (see below for the rules).

Alphabetise is released under the `MIT-0 licence
<https://choosealicense.com/licenses/mit-0/>`_. It is tested on Python 3.7+.

.. image:: https://github.com/tlocke/flake8-alphabetize/actions/workflows/test.yaml/badge.svg
   :alt: Build Status

.. contents:: Table of Contents
   :depth: 1
   :local:


Installation
------------

1. Create a virtual environment: ``python3 -m venv venv``

#. Activate it: ``source venv/bin/activate``

2. Install: ``pip install flake8-alphabetize``


Examples
--------

Say we have a Python file ``myfile.py``:

.. code:: python

   from datetime import time, date

   print(time(9, 39), date(2021, 4, 11))


by running the command ``flake8`` we'll get::

   myfile.py:1:1: AZ200 Imported names are in the wrong order. Should be date, time

We can tell Alphabetize what the package name is, and then it'll know that its imports
should be in a group at the bottom of the imports. Here's an example:

.. code:: python

   import uuid

   from myapp import myfunc

   print(uuid.UUID4(), myfunc())


by running the command ``flake8 --application-names myapp`` we won't get any errors.


Usage
-----

As you use Flake8 in the normal way, Alphabetize will report errors using the following
codes:

.. table:: Error Codes

   +-------+----------------------------------------------------------------+
   | Code  | Error Type                                                     |
   +=======+================================================================+
   | AZ100 | Import statements are in the wrong order                       |
   +-------+----------------------------------------------------------------+
   | AZ200 | The names in the ``import from`` are in the wrong order        |
   +-------+----------------------------------------------------------------+
   | AZ300 | Two ``import from`` statements must be combined.               |
   +-------+----------------------------------------------------------------+
   | AZ400 | The names in the ``__all__`` are in the wrong order            |
   +-------+----------------------------------------------------------------+

Alphabetize follows the Black formatter's uncompromising approach and so there's only
one configuration option which is ``application-names``. This is a comma-separated list
of top-level, package names that are to be treated as application imports, eg. 'myapp'.
Since Alphabetize is a Flake8 plugin, this configuration option is set using
`Flake8 configuration <https://flake8.pycqa.org/en/latest/user/configuration.html>`_.


Rules Of Import Ordering
------------------------

Here are the ordering rules that Alphabetize follows:

1. The special case ``from __future__`` import comes first.

#. Imports from the standard library come next, followed by third party imports,
   followed by application imports.

#. Relative imports are assumed to be application imports.

#. The standard library group has ``import`` statements first (in alphabetical order),
   followed by ``from import`` statements (in alphabetical order).

#. The third party group is further grouped by library name. Then each library subgroup
   has ``import`` statements first (in alphabetical order), followed by ``from import``
   statements (in alphabetical order).

#. The application group is further grouped by import level, with absolute imports first
   and then relative imports of increasing level. Within each level, the imports should
   be ordered by library name. Then each library subgroup has ``import`` statements
   first (in alphabetical order), followed by ``from import`` statements (in
   alphabetical order).

#. ``from import`` statements for the same library must be combined.

#. Alphabetize only looks at imports at the module level, any imports within the code
   are ignored.


Doing A Release Of Alphabetize
------------------------------

Run ``tox`` to make sure all tests pass, then update the release notes, then do::

   git tag -a x.y.z -m "version x.y.z"
   rm -r build; rm -r dist
   python -m build
   twine upload --sign dist/*


Release Notes
-------------


Version 0.0.17, 2021-11-17
``````````````````````````

* Handle the case of an ``__all__`` being a ``tuple``.


Version 0.0.16, 2021-07-26
``````````````````````````

* Don't perform any import order checks if there are multiple imports on a line, as
  this will be reported by Flake8. Once the Flake8 error has been fixed, checks can
  continue.


Version 0.0.15, 2021-06-17
``````````````````````````

* Fix bug where the ``--application-names`` command line option failed with a
  comma-separated list.


Version 0.0.14, 2021-04-20
``````````````````````````

* Fix bug where ``from . import logging`` appears in message as ``from .None import
  logging``.


Version 0.0.13, 2021-04-20
``````````````````````````

* Fix bug where it fails on a relative import such as ``from . import logging``.


Version 0.0.12, 2021-04-12
``````````````````````````

* Check the order of the elements of ``__all__``.


Version 0.0.11, 2021-04-11
``````````````````````````

* Order application imports by import level, absolute imports at the top.


Version 0.0.10, 2021-04-11
``````````````````````````

* Fix bug where potentially fails with > 2 imports.


Version 0.0.9, 2021-04-11
`````````````````````````

* There's a clash of option names, so now application imports can now be identified by
  setting the ``application-names`` configuration option.


Version 0.0.8, 2021-04-11
`````````````````````````

* Application imports can now be identified by setting the ``application-package-names``
  configuration option.


Version 0.0.7, 2021-04-10
`````````````````````````

* Import of ``__future__``. Should always be first.


Version 0.0.6, 2021-04-10
`````````````````````````

* Third party libraries should be grouped by top-level name.


Version 0.0.5, 2021-04-10
`````````````````````````

* Take into account whether a module is in the standard library or not.


Version 0.0.4, 2021-04-10
`````````````````````````

* Make entry point AZ instead of ALP.


Version 0.0.3, 2021-04-10
`````````````````````````

* Check the order within ``from import`` statements.


Version 0.0.2, 2021-04-09
`````````````````````````

* Partially support ``from import`` statements.


Version 0.0.1, 2021-04-09
`````````````````````````

* Now partially supports ``import`` statements.


Version 0.0.0, 2021-04-09
`````````````````````````

* Initial release. Doesn't do much at this stage.
