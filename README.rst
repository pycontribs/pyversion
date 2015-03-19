Python Version Library
======================
|Downloads|_ |Badge|_ |Egg|_ |Wheel|_ |License|_

.. |Badge| image:: https://pypip.in/v/pyversion/badge.png
.. _Badge: https://pypi.python.org/pypi/pyversion/
.. |Downloads| image:: https://pypip.in/d/pyversion/badge.png
.. _Downloads: https://pypi.python.org/pypi/pyversion/
.. |Egg| image:: https://pypip.in/egg/pyversion/badge.png
.. _Egg: https://pypi.python.org/pypi/pyversion/
.. |Wheel| image:: https://pypip.in/wheel/pyversion/badge.png
.. _Wheel: https://pypi.python.org/pypi/pyversion/
.. |License| image:: https://pypip.in/license/pyversion/badge.png
.. _License: https://pypi.python.org/pypi/pyversion/

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
