import os
from setuptools import setup
from pbr import util

kwargs = util.cfg_to_args()
kwargs["auto_version"] = "PBR"

setup(**kwargs)
