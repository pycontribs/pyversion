import os
import re
import setuptools.command.egg_info as orig
from .version import Version, VersionUtils

__all__ = ['increment']

class increment(orig.egg_info):
    """ """
    description = "Will increment the version indentifier"
    user_options = orig.egg_info.user_options
    
    def tagged_version(self):
        version = VersionUtils.get_version(self.distribution.get_name())
        next_version = VersionUtils.increment(version)
        output = os.environ.get('RELEASE_VERSION', str(next_version))
        print "Automatically Setting Version to:", output
        return output

    def run(self):
        """Will increment the current version number next release version as requested by RELEASE_TYPE"""
        orig.egg_info.run(self)
        
