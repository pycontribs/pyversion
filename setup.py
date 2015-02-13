import os
from setuptools import setup
from pbr import util
import version

os.environ['PBR_VERSION'] = str(version.__version__)
setup(
    setup_requires=['pbr'],
    pbr=True,
)
