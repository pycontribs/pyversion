import os
import re
import setuptools.command.test as o
import setuptools.command.egg_info as orig
from distutils import log as logger
from .version import Version, VersionUtils

__all__ = ['increment']

class increment(orig.egg_info):
    """ """
    description = "Will increment the version indentifier"
    user_options = orig.egg_info.user_options + [('release-type=', None, "The Release Type to increment by (default: micro)"),
                                                 ('release-version=', None, "The Release Version to override to NOTE: no increment will happen (default: None)")]
    
    def initialize_options(self):
        orig.egg_info.initialize_options(self)      
        self.release_version = os.environ.get('RELEASE_VERSION', None)
        self.release_type = os.environ.get('RELEASE_TYPE', 'micro')
        

    def finalize_options(self):
        print self.release_version, self.release_type
        orig.egg_info.finalize_options(self)
    
    def tagged_version(self):
        os.environ['RELEASE_TYPE'] = self.release_type
        if self.release_version is None:
            version = VersionUtils.get_version(self.distribution.get_name())
            self.release_version = VersionUtils.increment(version)
        logger.info("Automatically Setting Version to: {0}".format(self.release_version))
        return self.release_version

    def run(self):
        """Will increment the current version number next release version as requested by RELEASE_TYPE"""
        orig.egg_info.run(self)
        
