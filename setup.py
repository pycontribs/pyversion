import os
from setuptools import setup

setup(
    setup_requires=[
        'pip>=6.0.8',
        'pbr',
        'pyversion'
    ],
    pbr=True,
    auto_version="PBR",
)
