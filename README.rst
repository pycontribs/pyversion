Python Version Library
======================

.. image:: https://badge.fury.io/py/pyversion.svg
    :target: https://badge.fury.io/py/pyversion3
    :alt: Current Version

.. image:: https://travis-ci.org/lingster/pyversion3.svg
    :target: https://travis-ci.org/lingster/pyversion3
    :alt: Build Status

.. image:: https://coveralls.io/repos/lingster/pyversion3/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/lingster/pyversion3?branch=master
    :alt: Coverage

.. image:: https://requires.io/github/lingster/pyversionr/requirements.svg?branch=master
     :target: https://requires.io/github/lingster/pyversion3/requirements/?branch=master
     :alt: Requirements Status

Python package versioning made simple

NOTE: this is a fork of the original rocktavious/pyversion. This version has been upgraded to support python3.x

Quickstart
----------
Feeling impatient? I like your style.

In your setup.py file

.. code-block:: python

    setup(
        ...
        setup_requires = ['pyversion'],
        auto_version = True,
        ...
    )

On the command line

.. code-block:: python

    python setup.py increment tag register sdist upload


PBR
---

If you are also using the openstack PBR package pyversion supports this as well
just modify your setup.py file

.. code-block:: python

    setup(
        setup_requires = [
            'pbr',
            'pyversion'
        ],
        pbr = True,
        auto_version = "PBR",
    )

Installation
------------
Download and install using `pip install pyversion`

CLI
---
The package also comes with a cli command that can be used to determine what
the current version the package sees for your package

usage:

.. code-block:: bash

    >>> pyversion <name of your package>
    1.2.3

Developing
----------
To develop on this project, please take a fork of then and submit a pull requeest once changes are ready.

This package makes of of pipenv for installing and dependency maintainence.
If publishing to pypi, rememeber to update requirements.txt and test-requirements.txt as follows:

     pipenv install --dev -ignore-pipfile > requirements.txt
     pipenv lock --requirements > requirements.txt

Also remember to run tox in the base directory to run black, linter and other tests.

python setup.py sdist bdist_wheelA
twine upload dist/*



