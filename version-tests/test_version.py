import os
import operator
import unittest2 as unittest

from version import *


class TestSemanticVersion(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.version = Version('pyversion')
        cls.v1 = parse_version('1!1.2.3')
        cls.v2 = parse_version('1.2.3.post2')
        cls.v3 = parse_version('1.2.3.a1')
        cls.v4 = parse_version('1.2.a1')
        cls.v5 = parse_version('2014b')
        cls.v6 = parse_version('2.1.3.45.654')
        cls.v7 = parse_version('1.2.3.g39485hdjk')
    
    def test_version_obj(self):
        v = Version('pyversion')
        v2 = VersionUtils.increment(v)
        self.assertNotEqual(v, v2)
        self.assertEquals(v, self.version)
        
    def test_unknown_package(self):
        v = Version('jd85kd9f0')
        v2 = VersionUtils.increment(v)
        self.assertNotEqual(v, v2)
        
    def test_release_version_override(self):
        os.environ['RELEASE_VERSION'] = "2.4.5.6.7.8"
        v = Version('pyversion')
        v2 = VersionUtils.increment(v)
        self.assertNotEqual(v, v2)
        self.assertEquals(v, self.version)
        self.assertEquals(v2, '2.4.5.6.7.8')
        
    def test_increment_epoch(self):
        os.environ['RELEASE_TYPE'] = "epoch"
        v1 = VersionUtils.increment(self.v1)
        v2 = VersionUtils.increment(self.v2)
        v3 = VersionUtils.increment(self.v3)
        v4 = VersionUtils.increment(self.v4)
        v5 = VersionUtils.increment(self.v5)
        v6 = VersionUtils.increment(self.v6)
        self.assertEquals(v1, '2!1.0.0')
        self.assertEquals(v2, '1!1.0.0')
        self.assertEquals(v3, '1!1.0.0')
        self.assertEquals(v4, '1!1.0.0')
        self.assertEquals(v5, '1!1.0.0')
        self.assertEquals(v6, '1!1.0.0')

    def test_increment_micro(self):
        os.environ['RELEASE_TYPE'] = "micro"
        v1 = VersionUtils.increment(self.v1)
        v2 = VersionUtils.increment(self.v2)
        v3 = VersionUtils.increment(self.v3)
        v4 = VersionUtils.increment(self.v4)
        v5 = VersionUtils.increment(self.v5)
        v6 = VersionUtils.increment(self.v6)
        self.assertEquals(v1, '1!1.2.4')
        self.assertEquals(v2, '1.2.4')
        self.assertEquals(v3, '1.2.3')
        self.assertEquals(v4, '1.2.1')
        self.assertEquals(v5, '2014.0.1')
        self.assertEquals(v6, '2.1.4')
        
    def test_increment_minor(self):
        os.environ['RELEASE_TYPE'] = "minor"
        v1 = VersionUtils.increment(self.v1)
        v2 = VersionUtils.increment(self.v2)
        v3 = VersionUtils.increment(self.v3)
        v4 = VersionUtils.increment(self.v4)
        v5 = VersionUtils.increment(self.v5)
        v6 = VersionUtils.increment(self.v6)
        self.assertEquals(v1, '1!1.3.0')
        self.assertEquals(v2, '1.3.0')
        self.assertEquals(v3, '1.3.0')
        self.assertEquals(v4, '1.3')
        self.assertEquals(v5, '2014.1')
        self.assertEquals(v6, '2.2.0')
        
    def test_increment_major(self):
        os.environ['RELEASE_TYPE'] = "major"
        v1 = VersionUtils.increment(self.v1)
        v2 = VersionUtils.increment(self.v2)
        v3 = VersionUtils.increment(self.v3)
        v4 = VersionUtils.increment(self.v4)
        v5 = VersionUtils.increment(self.v5)
        v6 = VersionUtils.increment(self.v6)
        self.assertEquals(v1, '1!2.0.0')
        self.assertEquals(v2, '2.0.0')
        self.assertEquals(v3, '2.0.0')
        self.assertEquals(v4, '2.0')
        self.assertEquals(v5, '2015')
        self.assertEquals(v6, '3.0.0')
        
    def test_increment_pre_release(self):
        os.environ['RELEASE_TYPE'] = "pre"
        v1 = VersionUtils.increment(self.v1)
        v2 = VersionUtils.increment(self.v2)
        v3 = VersionUtils.increment(self.v3)
        v4 = VersionUtils.increment(self.v4)
        v5 = VersionUtils.increment(self.v5)
        v6 = VersionUtils.increment(self.v6)
        self.assertEquals(v1, '1!1.2.4.pre1')
        self.assertEquals(v2, '1.2.4.pre1')
        self.assertEquals(v3, '1.2.3a2')
        self.assertEquals(v4, '1.2a2')
        self.assertEquals(v5, '2014b1')
        self.assertEquals(v6, '2.1.4.pre1')
        
    def test_increment_dev_release(self):
        os.environ['RELEASE_TYPE'] = "dev"
        v1 = VersionUtils.increment(self.v1)
        v2 = VersionUtils.increment(self.v2)
        v3 = VersionUtils.increment(self.v3)
        v4 = VersionUtils.increment(self.v4)
        v5 = VersionUtils.increment(self.v5)
        v6 = VersionUtils.increment(self.v6)
        self.assertEquals(v1, '1!1.2.3.dev1')
        self.assertEquals(v2, '1.2.3.post2.dev1')
        self.assertEquals(v3, '1.2.3a1.dev1')
        self.assertEquals(v4, '1.2a1.dev1')
        self.assertEquals(v5, '2014b.dev1')
        self.assertEquals(v6, '2.1.3.45.654.dev1')
        
    def test_increment_post_release(self):
        os.environ['RELEASE_TYPE'] = "post"
        v1 = VersionUtils.increment(self.v1)
        v2 = VersionUtils.increment(self.v2)
        v3 = VersionUtils.increment(self.v3)
        v4 = VersionUtils.increment(self.v4)
        v5 = VersionUtils.increment(self.v5)
        v6 = VersionUtils.increment(self.v6)
        self.assertEquals(v1, '1!1.2.3.post1')
        self.assertEquals(v2, '1.2.3.post3')
        self.assertEquals(v3, '1.2.3a1.post1')
        self.assertEquals(v4, '1.2a1.post1')
        self.assertEquals(v5, '2014b.post1')
        self.assertEquals(v6, '2.1.3.45.654.post1')

    def test_legacy_version(self):
        with self.assertRaises(Exception):
            VersionUtils.increment(self.v7)
        
        
        
