Python Version Library
======================

.. image:: https://badge.fury.io/py/pyversion3.svg
    :target: https://badge.fury.io/py/pyversion3
    :alt: Current Version

.. image:: https://travis-ci.org/lingster/pyversion3.svg
    :target: https://travis-ci.org/lingster/pyversion3
    :alt: Build Status

.. image:: https://coveralls.io/repos/github/lingster/pyversion3/badge.svg?branch=master
    :target: https://coveralls.io/github/lingster/pyversion3?branch=master
    :alt: Coverage

.. image:: https://requires.io/github/lingster/pyversion3/requirements.svg?branch=master
    :target: https://requires.io/github/lingster/pyversion3/requirements/?branch=master
    :alt: Requirements Status

.. image:: https://snyk.io/test/github/lingster/pyversion3/badge.svg?targetFile=requirements.txt
    :target: https://snyk.io/test/github/lingster/pyversion3?targetFile=requirements.txt
    :alt: Vulnerabililtes Status

Python package versioning made simple

NOTE: this is a fork of the original rocktavious/pyversion. This version has been upgraded to support python3.x

Quickstart
----------
Feeling impatient? I like your style.

In your setup.py file

.. code-block:: python

    setup(
        ...
        setup_requires = ['pyversion3'],
        auto_version = True,
        ...
    )

On the command line

.. code-block:: python

    python setup.py increment tag register sdist upload


PBR
---

If you are also using the openstack PBR package pyversion3 supports this as well
just modify your setup.py file

.. code-block:: python

    setup(
        setup_requires = [
            'pbr',
            'pyversion3'
        ],
        pbr = True,
        auto_version = "PBR",
    )

Installation
------------
Download and install using `pip install pyversion3`

CLI
---
The package also comes with a cli command that can be used to determine what
the current version the package sees for your package

usage:

.. code-block:: bash

    >>> pyversion3 <name of your package>
    1.2.3

Developing
----------
To develop on this project, please take a fork of then and submit a pull requeest once changes are ready.

This package makes of of pipenv for installing and dependency maintainence.
If publishing to pypi, rememeber to update requirements.txt and test-requirements.txt as follows:

     pipenv install --dev -ignore-pipfile > requirements.txt
     pipenv lock --requirements > requirements.txt

Also remember to run tox in the base directory to run black, linter and other tests.

You can also run `tox` to perform black formatting, linting and testing. 
To test build and upload to test.pypi.org use:
`tox -e testrelease`

To build and upload to production use:
`tox -e release` will release to pypi a new version 

Travis is in use for CI, so you can also run: `travis-lint .travis.yml`

Or use the below to manully upload:
`python setup.py sdist bdist_wheel
twine upload dist/*`


