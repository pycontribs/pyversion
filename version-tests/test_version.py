import os
import operator
import unittest2 as unittest

from version import *


class TestSemanticVersion(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        self.version = Version('version')
        self.v1 = parse_version('1!1.2.3')
        self.v2 = parse_version('1.2.3.dev2.post1')
        self.v3 = parse_version('1.2.3.a1')
    
    def test_version_obj(self):
        v = Version('version')
        v2 = VersionUtils.increment(v)
        self.assertNotEqual(v, v2)
        self.assertEquals(v, self.version)

    def test_increment_micro(self):
        v1 = VersionUtils.increment(self.v1)
        v2 = VersionUtils.increment(self.v2)
        v3 = VersionUtils.increment(self.v3)
        self.assertEquals(v1, '1.2.4')
        self.assertEquals(v2, '1.2.4')
        self.assertEquals(v3, '1.2.4')
        
        
        
