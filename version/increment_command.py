import os
import re
from distutils.core import Command
from distutils import log as logger
from .version import Version, VersionUtils

__all__ = ['increment']

class increment(Command):
    """ """
    description = "Will increment the version indentifier"

    def run(self):
        """Will tag the currently active git commit id with the next release tag id"""
        version = VersionUtils.get_version(self.distribution.get_name())
        next_version = VersionUtils.increment(version)
        
