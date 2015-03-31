import os
from setuptools import setup

setup(
    setup_requires=[
        'packaging==15.0',
        'pbr==0.10.7',
        'pyversion',
    ],
    pbr=True,
    auto_version="PBR",
)
