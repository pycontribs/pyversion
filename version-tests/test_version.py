import operator
import unittest2 as unittest

from version import SemanticVersion


from_pip_string = SemanticVersion.from_pip_string


class TestSemanticVersion(unittest.TestCase):

    def test_equality(self):
        base = SemanticVersion(1, 2, 3)
        base2 = SemanticVersion(1, 2, 3)
        major = SemanticVersion(2, 2, 3)
        minor = SemanticVersion(1, 3, 3)
        patch = SemanticVersion(1, 2, 4)
        pre_base = SemanticVersion(1, 2, 3, 'a', 4)
        pre_base2 = SemanticVersion(1, 2, 3, 'a', 4)
        pre_type = SemanticVersion(1, 2, 3, 'b', 4)
        pre_serial = SemanticVersion(1, 2, 3, 'a', 5)
        dev_base = SemanticVersion(1, 2, 3, dev_count=6, githash='6')
        dev_base2 = SemanticVersion(1, 2, 3, dev_count=6, githash='6')
        dev_count = SemanticVersion(1, 2, 3, dev_count=7, githash='6')
        githash = SemanticVersion(1, 2, 3, dev_count=6, githash='7')
        self.assertEqual(base, base2)
        self.assertNotEqual(base, major)
        self.assertNotEqual(base, minor)
        self.assertNotEqual(base, patch)
        self.assertNotEqual(base, pre_type)
        self.assertNotEqual(base, pre_serial)
        self.assertNotEqual(base, dev_count)
        self.assertNotEqual(base, githash)
        self.assertEqual(pre_base, pre_base2)
        self.assertNotEqual(pre_base, pre_type)
        self.assertNotEqual(pre_base, pre_serial)
        self.assertNotEqual(pre_base, dev_count)
        self.assertNotEqual(pre_base, githash)
        self.assertEqual(dev_base, dev_base2)
        self.assertNotEqual(dev_base, dev_count)
        self.assertNotEqual(dev_base, githash)
        simple = SemanticVersion(1)
        explicit_minor = SemanticVersion(1, 0)
        explicit_patch = SemanticVersion(1, 0, 0)
        self.assertEqual(simple, explicit_minor)
        self.assertEqual(simple, explicit_patch)
        self.assertEqual(explicit_minor, explicit_patch)

    def test_ordering(self):
        base = SemanticVersion(1, 2, 3)
        major = SemanticVersion(2, 2, 3)
        minor = SemanticVersion(1, 3, 3)
        patch = SemanticVersion(1, 2, 4)
        pre_alpha = SemanticVersion(1, 2, 3, 'a', 4)
        pre_beta = SemanticVersion(1, 2, 3, 'b', 3)
        pre_rc = SemanticVersion(1, 2, 3, 'rc', 2)
        pre_serial = SemanticVersion(1, 2, 3, 'a', 5)
        dev_base = SemanticVersion(1, 2, 3, dev_count=6, githash='6')
        dev_count = SemanticVersion(1, 2, 3, dev_count=7, githash='6')
        githash = SemanticVersion(1, 2, 3, dev_count=6, githash='7')
        self.assertLess(base, major)
        self.assertLess(base, minor)
        self.assertLess(base, patch)
        self.assertGreater(base, pre_alpha)
        self.assertGreater(base, dev_base)
        self.assertGreater(major, base)
        self.assertGreater(minor, base)
        self.assertGreater(patch, base)
        self.assertLess(dev_base, base)
        self.assertGreater(pre_beta, pre_alpha)
        self.assertLess(pre_beta, pre_rc)
        self.assertGreater(pre_beta, pre_serial)
        self.assertLess(pre_alpha, base)
        self.assertLess(pre_alpha, pre_beta)
        self.assertLess(pre_alpha, pre_serial)
        self.assertGreater(pre_rc, pre_beta)
        self.assertGreater(pre_serial, pre_alpha)
        self.assertLess(pre_serial, pre_beta)
        self.assertLess(dev_base, dev_count)
        self.assertGreater(dev_count, dev_base)
        self.assertRaises(TypeError, operator.lt, pre_alpha, dev_base)
        self.assertRaises(TypeError, operator.lt, dev_base, pre_alpha)
        self.assertRaises(TypeError, operator.lt, dev_base, githash)

    def test_from_pip_string_legacy_alpha(self):
        expected = SemanticVersion(
            1, 2, 0, prerelease_type='rc', prerelease=1)
        parsed = from_pip_string('1.2.0rc1')
        self.assertEqual(expected, parsed)

    def test_from_pip_string_legacy_nonzero_lead_in(self):
        # reported in bug 1361251
        expected = SemanticVersion(
            0, 0, 1, prerelease_type='a', prerelease=2)
        parsed = from_pip_string('0.0.1a2')
        self.assertEqual(expected, parsed)

    def test_from_pip_string_legacy_short_nonzero_lead_in(self):
        expected = SemanticVersion(
            0, 1, 0, prerelease_type='a', prerelease=2)
        parsed = from_pip_string('0.1a2')
        self.assertEqual(expected, parsed)

    def test_from_pip_string_legacy_no_0_prerelease(self):
        expected = SemanticVersion(
            2, 1, 0, prerelease_type='rc', prerelease=1)
        parsed = from_pip_string('2.1.0.rc1')
        self.assertEqual(expected, parsed)

    def test_from_pip_string_legacy_no_0_prerelease_2(self):
        expected = SemanticVersion(
            2, 0, 0, prerelease_type='rc', prerelease=1)
        parsed = from_pip_string('2.0.0.rc1')
        self.assertEqual(expected, parsed)

    def test_from_pip_string_legacy_non_440_beta(self):
        expected = SemanticVersion(
            2014, 2, prerelease_type='b', prerelease=2)
        parsed = from_pip_string('2014.2.b2')
        self.assertEqual(expected, parsed)

    def test_from_pip_string_legacy_dev(self):
        expected = SemanticVersion(
            0, 10, 1, dev_count=3, githash='83bef74')
        parsed = from_pip_string('0.10.1.3.g83bef74')
        self.assertEqual(expected, parsed)

    def test_from_pip_string_legacy_corner_case_dev(self):
        # If the last tag is missing, or if the last tag has less than 3
        # components, we need to 0 extend on parsing.
        expected = SemanticVersion(
            0, 0, 0, dev_count=1, githash='83bef74')
        parsed = from_pip_string('0.0.g83bef74')
        self.assertEqual(expected, parsed)

    def test_from_pip_string_legacy_short_dev(self):
        # If the last tag is missing, or if the last tag has less than 3
        # components, we need to 0 extend on parsing.
        expected = SemanticVersion(
            0, 0, 0, dev_count=1, githash='83bef74')
        parsed = from_pip_string('0.g83bef74')
        self.assertEqual(expected, parsed)

    def test_from_pip_string_dev_missing_patch_version(self):
        expected = SemanticVersion(
            2014, 2, dev_count=21, githash='c4c8d0b')
        parsed = from_pip_string('2014.2.dev21.gc4c8d0b')
        self.assertEqual(expected, parsed)

    def test_from_pip_string_pure_git_hash(self):
        self.assertRaises(ValueError, from_pip_string, '6eed5ae')

    def test_final_version(self):
        semver = SemanticVersion(1, 2, 3)
        self.assertEqual((1, 2, 3, 'final', 0), semver.version_tuple())
        self.assertEqual("1.2.3", semver.brief_string())
        self.assertEqual("1.2.3", semver.debian_string())
        self.assertEqual("1.2.3", semver.release_string())
        self.assertEqual("1.2.3", semver.rpm_string())
        self.assertEqual(semver, from_pip_string("1.2.3"))

    def test_parsing_short_forms(self):
        semver = SemanticVersion(1, 0, 0)
        self.assertEqual(semver, from_pip_string("1"))
        self.assertEqual(semver, from_pip_string("1.0"))
        self.assertEqual(semver, from_pip_string("1.0.0"))

    def test_dev_version(self):
        semver = SemanticVersion(1, 2, 4, dev_count=5, githash='12')
        self.assertEqual((1, 2, 4, 'dev', 4), semver.version_tuple())
        self.assertEqual("1.2.4", semver.brief_string())
        self.assertEqual("1.2.4~dev5+g12", semver.debian_string())
        self.assertEqual("1.2.4.dev5.g12", semver.release_string())
        self.assertEqual("1.2.3.dev5+g12", semver.rpm_string())
        self.assertEqual(semver, from_pip_string("1.2.4.dev5.g12"))

    def test_dev_no_git_version(self):
        semver = SemanticVersion(1, 2, 4, dev_count=5)
        self.assertEqual((1, 2, 4, 'dev', 4), semver.version_tuple())
        self.assertEqual("1.2.4", semver.brief_string())
        self.assertEqual("1.2.4~dev5", semver.debian_string())
        self.assertEqual("1.2.4.dev5", semver.release_string())
        self.assertEqual("1.2.3.dev5", semver.rpm_string())
        self.assertEqual(semver, from_pip_string("1.2.4.dev5"))

    def test_dev_zero_version(self):
        semver = SemanticVersion(1, 2, 0, dev_count=5)
        self.assertEqual((1, 2, 0, 'dev', 4), semver.version_tuple())
        self.assertEqual("1.2.0", semver.brief_string())
        self.assertEqual("1.2.0~dev5", semver.debian_string())
        self.assertEqual("1.2.0.dev5", semver.release_string())
        self.assertEqual("1.1.9999.dev5", semver.rpm_string())
        self.assertEqual(semver, from_pip_string("1.2.0.dev5"))

    def test_alpha_dev_version(self):
        self.assertRaises(
            ValueError, SemanticVersion, 1, 2, 4, 'a', 1, 5, '12')

    def test_alpha_version(self):
        semver = SemanticVersion(1, 2, 4, 'a', 1)
        self.assertEqual((1, 2, 4, 'alpha', 1), semver.version_tuple())
        self.assertEqual("1.2.4", semver.brief_string())
        self.assertEqual("1.2.4~a1", semver.debian_string())
        self.assertEqual("1.2.4.0a1", semver.release_string())
        self.assertEqual("1.2.3.a1", semver.rpm_string())
        self.assertEqual(semver, from_pip_string("1.2.4.0a1"))

    def test_alpha_zero_version(self):
        semver = SemanticVersion(1, 2, 0, 'a', 1)
        self.assertEqual((1, 2, 0, 'alpha', 1), semver.version_tuple())
        self.assertEqual("1.2.0", semver.brief_string())
        self.assertEqual("1.2.0~a1", semver.debian_string())
        self.assertEqual("1.2.0.0a1", semver.release_string())
        self.assertEqual("1.1.9999.a1", semver.rpm_string())
        self.assertEqual(semver, from_pip_string("1.2.0.0a1"))

    def test_alpha_major_zero_version(self):
        semver = SemanticVersion(1, 0, 0, 'a', 1)
        self.assertEqual((1, 0, 0, 'alpha', 1), semver.version_tuple())
        self.assertEqual("1.0.0", semver.brief_string())
        self.assertEqual("1.0.0~a1", semver.debian_string())
        self.assertEqual("1.0.0.0a1", semver.release_string())
        self.assertEqual("0.9999.9999.a1", semver.rpm_string())
        self.assertEqual(semver, from_pip_string("1.0.0.0a1"))

    def test_alpha_default_version(self):
        semver = SemanticVersion(1, 2, 4, 'a')
        self.assertEqual((1, 2, 4, 'alpha', 0), semver.version_tuple())
        self.assertEqual("1.2.4", semver.brief_string())
        self.assertEqual("1.2.4~a0", semver.debian_string())
        self.assertEqual("1.2.4.0a0", semver.release_string())
        self.assertEqual("1.2.3.a0", semver.rpm_string())
        self.assertEqual(semver, from_pip_string("1.2.4.0a0"))

    def test_beta_dev_version(self):
        self.assertRaises(
            ValueError, SemanticVersion, 1, 2, 4, 'b', 1, 5, '12')

    def test_beta_version(self):
        semver = SemanticVersion(1, 2, 4, 'b', 1)
        self.assertEqual((1, 2, 4, 'beta', 1), semver.version_tuple())
        self.assertEqual("1.2.4", semver.brief_string())
        self.assertEqual("1.2.4~b1", semver.debian_string())
        self.assertEqual("1.2.4.0b1", semver.release_string())
        self.assertEqual("1.2.3.b1", semver.rpm_string())
        self.assertEqual(semver, from_pip_string("1.2.4.0b1"))

    def test_decrement_nonrelease(self):
        # The prior version of any non-release is a release
        semver = SemanticVersion(1, 2, 4, 'b', 1)
        self.assertEqual(
            SemanticVersion(1, 2, 3), semver.decrement())

    def test_decrement_nonrelease_zero(self):
        # We set an arbitrary max version of 9999 when decrementing versions
        # - this is part of handling rpm support.
        semver = SemanticVersion(1, 0, 0)
        self.assertEqual(
            SemanticVersion(0, 9999, 9999), semver.decrement())

    def test_decrement_release(self):
        # The next patch version of a release version requires a change to the
        # patch level.
        semver = SemanticVersion(1, 2, 5)
        self.assertEqual(
            SemanticVersion(1, 2, 6), semver.increment())
        self.assertEqual(
            SemanticVersion(1, 3, 0), semver.increment(minor=True))
        self.assertEqual(
            SemanticVersion(2, 0, 0), semver.increment(major=True))

    def test_increment_nonrelease(self):
        # The next patch version of a non-release version is another
        # non-release version as the next release doesn't need to be
        # incremented.
        semver = SemanticVersion(1, 2, 4, 'b', 1)
        self.assertEqual(
            SemanticVersion(1, 2, 4, 'b', 2), semver.increment())
        # Major and minor increments however need to bump things.
        self.assertEqual(
            SemanticVersion(1, 3, 0), semver.increment(minor=True))
        self.assertEqual(
            SemanticVersion(2, 0, 0), semver.increment(major=True))

    def test_increment_release(self):
        # The next patch version of a release version requires a change to the
        # patch level.
        semver = SemanticVersion(1, 2, 5)
        self.assertEqual(
            SemanticVersion(1, 2, 6), semver.increment())
        self.assertEqual(
            SemanticVersion(1, 3, 0), semver.increment(minor=True))
        self.assertEqual(
            SemanticVersion(2, 0, 0), semver.increment(major=True))

    def test_rc_dev_version(self):
        self.assertRaises(
            ValueError, SemanticVersion, 1, 2, 4, 'rc', 1, 5, '12')

    def test_rc_version(self):
        semver = SemanticVersion(1, 2, 4, 'rc', 1)
        self.assertEqual((1, 2, 4, 'candidate', 1), semver.version_tuple())
        self.assertEqual("1.2.4", semver.brief_string())
        self.assertEqual("1.2.4~rc1", semver.debian_string())
        self.assertEqual("1.2.4.0rc1", semver.release_string())
        self.assertEqual("1.2.3.rc1", semver.rpm_string())
        self.assertEqual(semver, from_pip_string("1.2.4.0rc1"))

    def test_to_dev(self):
        self.assertEqual(
            SemanticVersion(1, 2, 3, dev_count=1, githash='foo'),
            SemanticVersion(1, 2, 3).to_dev(1, 'foo'))
        self.assertEqual(
            SemanticVersion(1, 2, 3, dev_count=1, githash='foo'),
            SemanticVersion(1, 2, 3, 'rc', 1).to_dev(1, 'foo'))

    def test_to_release(self):
        self.assertEqual(
            SemanticVersion(1, 2, 3),
            SemanticVersion(
                1, 2, 3, dev_count=1, githash='foo').to_release())
        self.assertEqual(
            SemanticVersion(1, 2, 3),
            SemanticVersion(1, 2, 3, 'rc', 1).to_release())
