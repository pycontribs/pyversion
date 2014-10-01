Python Version Library
======================
|Status|_ |Downloads|_ |Badge|_ |Egg|_ |Wheel|_ |License|_

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
.. |Status| image:: http://jenkins.rocktavious.com/buildStatus/icon?job=pyversion-master
.. _Status: http://jenkins.rocktavious.com/job/pyversion-master/

Python package versioning made simple

Quickstart
----------
Feeling impatient? I like your style.

::

        from version import Version
        
        __version__ = Version('project-name') #Version will be auto calculated
        
        python setup.py tag register sdist upload


Installation
------------
Download and install using `pip install pyversion` or `easy_install pyversion`
