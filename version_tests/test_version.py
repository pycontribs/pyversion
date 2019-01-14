import os
import unittest2 as unittest
import sys
from contextlib import contextmanager
from io import StringIO

from version.version3 import Version, VersionUtils, parse_version
from version.cli import main


class TestSemanticVersion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.version = Version("pyversion3")
        cls.v1 = parse_version("1!1.2.3")
        cls.v2 = parse_version("1.2.3.post2")
        cls.v3 = parse_version("1.2.3.a1")
        cls.v4 = parse_version("1.2.a1")
        cls.v5 = parse_version("2014b")
        cls.v6 = parse_version("2.1.3.45.654")
        cls.v7 = parse_version("1.2.3.g39485hdjk")

    def test_version_obj(self):
        v = Version("pyversion3")
        v2 = VersionUtils.increment(v)
        self.assertNotEqual(v, v2)
        self.assertEqual(v, self.version)

    def test_unknown_package(self):
        v = Version("jd85kd9f0")
        v2 = VersionUtils.increment(v)
        self.assertNotEqual(v, v2)

    def test_release_version_override(self):
        os.environ["RELEASE_VERSION"] = "2.4.5.6.7.8"
        v = Version("pyversion3")
        v2 = VersionUtils.increment(v)
        self.assertNotEqual(v, v2)
        self.assertEqual(v, self.version)
        self.assertEqual(v2, "2.4.5.6.7.8")

    def test_increment_epoch(self):
        os.environ["RELEASE_TYPE"] = "epoch"
        v1 = VersionUtils.increment(self.v1)
        v2 = VersionUtils.increment(self.v2)
        v3 = VersionUtils.increment(self.v3)
        v4 = VersionUtils.increment(self.v4)
        v5 = VersionUtils.increment(self.v5)
        v6 = VersionUtils.increment(self.v6)
        self.assertEqual(v1, "2!1.0.0")
        self.assertEqual(v2, "1!1.0.0")
        self.assertEqual(v3, "1!1.0.0")
        self.assertEqual(v4, "1!1.0.0")
        self.assertEqual(v5, "1!1.0.0")
        self.assertEqual(v6, "1!1.0.0")

    def test_increment_micro(self):
        os.environ["RELEASE_TYPE"] = "micro"
        v1 = VersionUtils.increment(self.v1)
        v2 = VersionUtils.increment(self.v2)
        v3 = VersionUtils.increment(self.v3)
        v4 = VersionUtils.increment(self.v4)
        v5 = VersionUtils.increment(self.v5)
        v6 = VersionUtils.increment(self.v6)
        self.assertEqual(v1, "1!1.2.4")
        self.assertEqual(v2, "1.2.4")
        self.assertEqual(v3, "1.2.3")
        self.assertEqual(v4, "1.2.1")
        self.assertEqual(v5, "2014.0.1")
        self.assertEqual(v6, "2.1.4")

    def test_increment_minor(self):
        os.environ["RELEASE_TYPE"] = "minor"
        v1 = VersionUtils.increment(self.v1)
        v2 = VersionUtils.increment(self.v2)
        v3 = VersionUtils.increment(self.v3)
        v4 = VersionUtils.increment(self.v4)
        v5 = VersionUtils.increment(self.v5)
        v6 = VersionUtils.increment(self.v6)
        self.assertEqual(v1, "1!1.3.0")
        self.assertEqual(v2, "1.3.0")
        self.assertEqual(v3, "1.3.0")
        self.assertEqual(v4, "1.3")
        self.assertEqual(v5, "2014.1")
        self.assertEqual(v6, "2.2.0")

    def test_increment_major(self):
        os.environ["RELEASE_TYPE"] = "major"
        v1 = VersionUtils.increment(self.v1)
        v2 = VersionUtils.increment(self.v2)
        v3 = VersionUtils.increment(self.v3)
        v4 = VersionUtils.increment(self.v4)
        v5 = VersionUtils.increment(self.v5)
        v6 = VersionUtils.increment(self.v6)
        self.assertEqual(v1, "1!2.0.0")
        self.assertEqual(v2, "2.0.0")
        self.assertEqual(v3, "2.0.0")
        self.assertEqual(v4, "2.0")
        self.assertEqual(v5, "2015")
        self.assertEqual(v6, "3.0.0")

    def test_increment_pre_release(self):
        os.environ["RELEASE_TYPE"] = "pre"
        v1 = VersionUtils.increment(self.v1)
        v2 = VersionUtils.increment(self.v2)
        v3 = VersionUtils.increment(self.v3)
        v4 = VersionUtils.increment(self.v4)
        v5 = VersionUtils.increment(self.v5)
        v6 = VersionUtils.increment(self.v6)
        self.assertEqual(v1, "1!1.2.4.pre1")
        self.assertEqual(v2, "1.2.4.pre1")
        self.assertEqual(v3, "1.2.3a2")
        self.assertEqual(v4, "1.2a2")
        self.assertEqual(v5, "2014b1")
        self.assertEqual(v6, "2.1.4.pre1")

    def test_increment_dev_release(self):
        os.environ["RELEASE_TYPE"] = "dev"
        v1 = VersionUtils.increment(self.v1)
        v2 = VersionUtils.increment(self.v2)
        v3 = VersionUtils.increment(self.v3)
        v4 = VersionUtils.increment(self.v4)
        v5 = VersionUtils.increment(self.v5)
        v6 = VersionUtils.increment(self.v6)

    @contextmanager
    def capture_output(self):
        new_out, new_err = StringIO(), StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = new_out, new_err
            yield sys.stdout, sys.stderr
        finally:
            sys.stdout, sys.stderr = old_out, old_err

    def test_cli_pypi_package(self):
        test_package = "flask-ask"
        with self.capture_output() as (out, err):
            main([test_package])
        output = out.getvalue().strip()
        self.assertEqual(
            output.split("\n")[0],
            f"get_version_from_pkg_resources: The '{test_package}' distribution was not found and is required by the application",
        )

        with self.capture_output() as (out, err):
            main([test_package, "increment"])
        output_inc = out.getvalue().strip()
        self.assertEqual(output_inc.split("\n")[1][:-1], output.split("\n")[1][:-1])

    def test_unknown_cli(self):
        test_package = "unknown_package"
        with self.capture_output() as (out, err):
            main([test_package])
        output = out.getvalue().strip()
        self.assertEqual(
            output.split("\n")[0],
            f"get_version_from_pkg_resources: The '{test_package}' distribution was not found and is required by the application",
        )
