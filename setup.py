from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from version import Version

setup(
    name='pyversion',
    version=Version('pyversion'),
    description='Python package versioning made simple',
    long_description=open("README.rst").read(),
    url='https://github.com/rocktavious/pyversion',
    author='Kyle Rockman',
    author_email='kyle.rockman@mac.com',
    license='MIT',
    keywords='pyversion version versioning packaging',
    packages=find_packages(exclude=['contrib', 'docs', 'pyversion-tests']),
    tests_require=open("test-requirements.txt").read().splitlines(),
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'distutils.commands': [
            'tag=version.tag_command:tag',
        ],
    },
)
