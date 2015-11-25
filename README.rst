Python Version Library
======================

.. image:: https://badge.fury.io/py/pyversion.svg
    :target: https://badge.fury.io/py/pyversion
    :alt: Current Version
    
.. image:: https://travis-ci.org/rocktavious/pyversion.svg
    :target: https://travis-ci.org/rocktavious/pyversion
    :alt: Build Status

.. image:: https://coveralls.io/repos/rocktavious/pyversion/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/rocktavious/pyversion?branch=master
    :alt: Coverage

.. image:: https://requires.io/github/rocktavious/pyversion/requirements.svg?branch=master
     :target: https://requires.io/github/rocktavious/pyversion/requirements/?branch=master
     :alt: Requirements Status

Python package versioning made simple

Quickstart
----------
Feeling impatient? I like your style.

In your setup.py file

::

        setup(
            ...
            setup_requires = ['pyversion'],
            auto_version = True,
            ...
        )
        

On the command line

::

        python setup.py increment tag register sdist upload


PBR
---

If you are also using the openstack PBR package pyversion supports this as well
just modify your setup.py file

::

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
