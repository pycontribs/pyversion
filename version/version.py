
#    Copyright 2012 OpenStack Foundation
#    Copyright 2012-2013 Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Utilities for consuming the version from pkg_resources.
"""
import os
import sys
import email
import subprocess
import itertools
import operator
import warnings
import pkg_resources

TRUE_VALUES = ('true', '1', 'yes')

def _is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
    
class VersionUtils(object):
    @staticmethod
    def get_boolean_option(option_dict, option_name, env_name):
        return ((option_name in option_dict
                 and option_dict[option_name][1].lower() in TRUE_VALUES) or
                str(os.getenv(env_name)).lower() in TRUE_VALUES)
    
    @staticmethod
    def iter_log_inner(git_dir):
        """Iterate over --oneline log entries.
    
        This parses the output intro a structured form but does not apply
        presentation logic to the output - making it suitable for different
        uses.
    
        :return: An iterator of (hash, tags_set, 1st_line) tuples.
        """
        log_cmd = ['log', '--oneline', '--decorate']
        changelog = VersionUtils.run_git_command(log_cmd, git_dir)
        for line in changelog.split('\n'):
            line_parts = line.split()
            if len(line_parts) < 2:
                continue
            # Tags are in a list contained in ()'s. If a commit
            # subject that is tagged happens to have ()'s in it
            # this will fail
            if line_parts[1].startswith('(') and ')' in line:
                msg = line.split(')')[1].strip()
            else:
                msg = " ".join(line_parts[1:])
    
            if "tag:" in line:
                tags = set([
                    tag.split(",")[0]
                    for tag in line.split(")")[0].split("tag: ")[1:]])
            else:
                tags = set()
    
            yield line_parts[0], tags, msg
            
    @staticmethod
    def iter_log_oneline(git_dir=None, option_dict=None):
        """Iterate over --oneline log entries if possible.
    
        This parses the output into a structured form but does not apply
        presentation logic to the output - making it suitable for different
        uses.
    
        :return: An iterator of (hash, tags_set, 1st_line) tuples, or None if
            changelog generation is disabled / not available.
        """
        if not option_dict:
            option_dict = {}
        should_skip = VersionUtils.get_boolean_option(option_dict, 'skip_changelog',
                                         'SKIP_WRITE_GIT_CHANGELOG')
        if should_skip:
            return
        if git_dir is None:
            git_dir = VersionUtils.get_git_directory()
        if not git_dir:
            return
        return VersionUtils.iter_log_inner(git_dir)    
    
    @staticmethod
    def run_shell_command(cmd, throw_on_error=False, buffer=True, env=None):
        if buffer:
            out_location = subprocess.PIPE
            err_location = subprocess.PIPE
        else:
            out_location = None
            err_location = None
    
        newenv = os.environ.copy()
        if env:
            newenv.update(env)
    
        output = subprocess.Popen(cmd,
                                  stdout=out_location,
                                  stderr=err_location,
                                  env=newenv)
        out = output.communicate()
        if output.returncode and throw_on_error:
            raise Exception("%s returned %d" % (cmd, output.returncode))
        if len(out) == 0 or not out[0] or not out[0].strip():
            return ''
        return out[0].strip().decode('utf-8')
    
    @staticmethod
    def run_git_command(cmd, git_dir, **kwargs):
        if not isinstance(cmd, (list, tuple)):
            cmd = [cmd]
        return VersionUtils.run_shell_command(
            ['git', '--git-dir=%s' % git_dir] + cmd, **kwargs)    
    
    @staticmethod
    def get_increment_kwargs(git_dir, tag):
        """Calculate the sort of semver increment needed from git history.
    
        Every commit from HEAD to tag is consider for Sem-Ver metadata lines.
    
        :return: a dict of kwargs for passing into SemanticVersion.increment.
        """
        result = {}
        if tag:
            version_spec = tag + "..HEAD"
        else:
            version_spec = "HEAD"
        changelog = VersionUtils.run_git_command(['log', version_spec], git_dir)
        header_len = len('    sem-ver:')
        commands = [line[header_len:].strip() for line in changelog.split('\n')
                    if line.lower().startswith('    sem-ver:')]
        symbols = set()
        for command in commands:
            symbols.update([symbol.strip() for symbol in command.split(',')])
    
        def _handle_symbol(symbol, symbols, impact):
            if symbol in symbols:
                result[impact] = True
                symbols.discard(symbol)
        _handle_symbol('bugfix', symbols, 'patch')
        _handle_symbol('feature', symbols, 'minor')
        _handle_symbol('deprecation', symbols, 'minor')
        _handle_symbol('api-break', symbols, 'major')
        # We don't want patch in the kwargs since it is not a keyword argument -
        # its the default minimum increment.
        result.pop('patch', None)
        return result
    
    @staticmethod
    def get_git_directory():
        return VersionUtils.run_shell_command(['git', 'rev-parse', '--git-dir'])
    
    @staticmethod
    def git_is_installed():
        try:
            # We cannot use 'which git' as it may not be available
            # in some distributions, So just try 'git --version'
            # to see if we run into trouble
            VersionUtils.run_shell_command(['git', '--version'])
        except OSError:
            return False
        return True
    
    @staticmethod
    def get_revno_and_last_tag(git_dir):
        """Return the commit data about the most recent tag.
    
        We use git-describe to find this out, but if there are no
        tags then we fall back to counting commits since the beginning
        of time.
        """
        changelog = VersionUtils.iter_log_oneline(git_dir=git_dir)
        row_count = 0
        for row_count, (ignored, tag_set, ignored) in enumerate(changelog):
            version_tags = set()
            for tag in list(tag_set):
                try:
                    version_tags.add(SemanticVersion.from_pip_string(tag))
                except Exception:
                    pass
            if version_tags:
                return max(version_tags).release_string(), row_count
        return "", row_count
    
    @staticmethod
    def get_version_from_git_target(git_dir, target_version):
        """Calculate a version from a target version in git_dir.
    
        This is used for untagged versions only. A new version is calculated as
        necessary based on git metadata - distance to tags, current hash, contents
        of commit messages.
    
        :param git_dir: The git directory we're working from.
        :param target_version: If None, the last tagged version (or 0 if there are
            no tags yet) is incremented as needed to produce an appropriate target
            version following semver rules. Otherwise target_version is used as a
            constraint - if semver rules would result in a newer version then an
            exception is raised.
        :return: A semver version object.
        """
        sha = VersionUtils.run_git_command(
            ['log', '-n1', '--pretty=format:%h'], git_dir)
        tag, distance = VersionUtils.get_revno_and_last_tag(git_dir)
        last_semver = SemanticVersion.from_pip_string(tag or '0')
        if distance == 0:
            new_version = last_semver
        else:
            new_version = last_semver.increment(
                **VersionUtils.get_increment_kwargs(git_dir, tag))
        if target_version is not None and new_version > target_version:
            raise ValueError(
                "git history requires a target version of %(new)s, but target "
                "version is %(target)s" %
                dict(new=new_version, target=target_version))
        if distance == 0:
            return last_semver
        if target_version is not None:
            return target_version.to_dev(distance, sha)
        else:
            return new_version.to_dev(distance, sha)
    
    @staticmethod
    def get_version_from_git(pre_version=None):
        """Calculate a version string from git.
    
        If the revision is tagged, return that. Otherwise calculate a semantic
        version description of the tree.
    
        The number of revisions since the last tag is included in the dev counter
        in the version for untagged versions.
    
        :param pre_version: If supplied use this as the target version rather than
            inferring one from the last tag + commit messages.
        """
        git_dir = VersionUtils.get_git_directory()
        if git_dir and VersionUtils.git_is_installed():
            try:
                tagged = VersionUtils.run_git_command(
                    ['describe', '--exact-match'], git_dir,
                    throw_on_error=True).replace('-', '.')
                target_version = SemanticVersion.from_pip_string(tagged)
            except Exception:
                if pre_version:
                    # not released yet - use pre_version as the target
                    target_version = SemanticVersion.from_pip_string(
                        pre_version)
                else:
                    # not released yet - just calculate from git history
                    target_version = None
            result = VersionUtils.get_version_from_git_target(git_dir, target_version)
            return result.release_string()
        # If we don't know the version, return an empty string so at least
        # the downstream users of the value always have the same type of
        # object to work with.
        try:
            return unicode()
        except NameError:
            return ''
    
    @staticmethod
    def get_version_from_pkg_metadata(package_name):
        """Get the version from package metadata if present.
    
        This looks for PKG-INFO if present (for sdists), and if not looks
        for METADATA (for wheels) and failing that will return None.
        """
        pkg_metadata_filenames = ['PKG-INFO', 'METADATA']
        pkg_metadata = {}
        for filename in pkg_metadata_filenames:
            try:
                pkg_metadata_file = open(filename, 'r')
            except (IOError, OSError):
                continue
            try:
                pkg_metadata = email.message_from_file(pkg_metadata_file)
            except email.MessageError:
                continue
    
        # Check to make sure we're in our own dir
        if pkg_metadata.get('Name', None) != package_name:
            return None
        return pkg_metadata.get('Version', None)
    
    @staticmethod
    def get_version(package_name, pre_version=None):
        """Get the version of the project. First, try getting it from PKG-INFO or
        METADATA, if it exists. If it does, that means we're in a distribution
        tarball or that install has happened. Otherwise, if there is no PKG-INFO
        or METADATA file, pull the version from git.
    
        :param pre_version: The version field from setup.cfg - if set then this
            version will be the next release.
        """
        version = os.environ.get("RELEASE_VERSION", None)
        if version:
            return version
        version = VersionUtils.get_version_from_pkg_metadata(package_name)
        if version:
            return version
        try:
            version = VersionUtils.get_version_from_git(pre_version)
            # Handle http://bugs.python.org/issue11638
            # version will either be an empty unicode string or a valid
            # unicode version string, but either way it's unicode and needs to
            # be encoded.
            if sys.version_info[0] == 2:
                version = version.encode('utf-8')
        except:
            pass
        if version:
            return version
        try:
            requirement = pkg_resources.Requirement.parse(package_name)
            provider = pkg_resources.get_provider(requirement)
            version = provider.version
        except:
            pass
        if version:
            return version
        
        warnings.warn("Versioning for this project requires an sdist, tarball, or access to an upstream git repository.  Defaulting the version to 0.0.1")
        return "0.0.1"


class SemanticVersion(object):
    """A pure semantic version independent of serialisation."""

    def __init__(self, major, minor=0, patch=0, prerelease_type=None,
                 prerelease=None, dev_count=None, githash=None):
        """Create a SemanticVersion.

        :param major: Major component of the version.
        :param minor: Minor component of the version. Defaults to 0.
        :param patch: Patch level component. Defaults to 0.
        :param prerelease_type: What sort of prerelease version this is -
            one of a(alpha), b(beta) or rc(release candidate).
        :param prerelease: For prerelease versions, what number prerelease.
            Defaults to 0.
        :param dev_count: How many commits since the last release.
        :param githash: What tree hash is this version for.

        :raises: ValueError if both a prerelease version and dev_count or
        githash are supplied. This is because semver does not permit both a prerelease version and a dev
        marker at the same time.
        """
        self._major = major
        self._minor = minor
        self._patch = patch
        self._prerelease_type = prerelease_type
        self._prerelease = prerelease
        if self._prerelease_type and not self._prerelease:
            self._prerelease = 0
        self._dev_count = dev_count
        self._githash = githash
        if prerelease_type is not None and dev_count is not None:
            raise ValueError(
                "invalid version: cannot have prerelease and dev strings %s %s"
                % (prerelease_type, dev_count))

    def __eq__(self, other):
        if not isinstance(other, SemanticVersion):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return sum(map(hash, self.__dict__.values()))

    def __lt__(self, other):
        """Compare self and other, another Semantic Version."""
        # NB(lifeless) this could perhaps be rewritten as
        # lt (tuple_of_one, tuple_of_other) with a single check for
        # the typeerror corner cases - that would likely be faster
        # if this ever becomes performance sensitive.
        if not isinstance(other, SemanticVersion):
            raise TypeError("ordering to non-SemanticVersion is undefined")
        this_tuple = (self._major, self._minor, self._patch)
        other_tuple = (other._major, other._minor, other._patch)
        if this_tuple < other_tuple:
            return True
        elif this_tuple > other_tuple:
            return False
        if self._prerelease_type:
            if other._prerelease_type:
                # Use the a < b < rc cheat
                this_tuple = (self._prerelease_type, self._prerelease)
                other_tuple = (other._prerelease_type, other._prerelease)
                return this_tuple < other_tuple
            elif other._dev_count:
                raise TypeError(
                    "ordering pre-release with dev builds is undefined")
            else:
                return True
        elif self._dev_count:
            if other._dev_count:
                if self._dev_count < other._dev_count:
                    return True
                elif self._dev_count > other._dev_count:
                    return False
                elif self._githash == other._githash:
                    # == it not <
                    return False
                raise TypeError(
                    "same version with different hash has no defined order")
            elif other._prerelease_type:
                raise TypeError(
                    "ordering pre-release with dev builds is undefined")
            else:
                return True
        else:
            # This is not pre-release.
            # If the other is pre-release or dev, we are greater, which is ! <
            # If the other is not pre-release, we are equal, which is ! <
            return False

    def __le__(self, other):
        return self == other or self < other

    def __ge__(self, other):
        return not self < other

    def __gt__(self, other):
        return not self <= other

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "SemanticVersion(%s)" % self.release_string()

    @classmethod
    def from_pip_string(klass, version_string):
        """Create a SemanticVersion from a pip version string.

        This method will parse a version like 1.3.0 into a SemanticVersion.

        Therefore: versions like 1.3.0a1 versions are handled, parsed into a
        canonical form and then output - resulting in 1.3.0.0a1.
        Dev versions like 0.10.1.3.g83bef74 will be parsed but
        output as 0.10.1.dev3.g83bef74.

        :raises ValueError: Never tagged versions sdisted result in
            just the git hash, e.g. '1234567' which poses a substantial problem
            since they collide with the semver versions when all the digits are
            numerals. Such versions will result in a ValueError being thrown if
            any non-numeric digits are present. They are an exception to the
            general case of accepting anything we ever output, since they were
            never intended and would permanently mess up versions on PyPI if
            ever released - we're treating that as a critical bug that we ever
            made them and have stopped doing that.
        """
        input_components = version_string.split('.')
        # decimals first (keep pre-release and dev/hashes to the right)
        components = [c for c in input_components if c.isdigit()]
        digit_len = len(components)
        if digit_len == 0:
            raise ValueError("Invalid version %r" % version_string)
        elif digit_len < 3:
            if (digit_len < len(input_components) and
                    input_components[digit_len][0].isdigit()):
                # Handle X.YaZ - Y is a digit not a leadin to pre-release.
                mixed_component = input_components[digit_len]
                last_component = ''.join(itertools.takewhile(
                    lambda x: x.isdigit(), mixed_component))
                components.append(last_component)
                input_components[digit_len:digit_len + 1] = [
                    last_component, mixed_component[len(last_component):]]
                digit_len += 1
            components.extend([0] * (3 - digit_len))
        components.extend(input_components[digit_len:])
        major = int(components[0])
        minor = int(components[1])
        dev_count = None
        prerelease_type = None
        prerelease = None
        githash = None

        def _parse_type(segment):
            # Discard leading digits (the 0 in 0a1)
            isdigit = operator.methodcaller('isdigit')
            segment = ''.join(itertools.dropwhile(isdigit, segment))
            isalpha = operator.methodcaller('isalpha')
            prerelease_type = ''.join(itertools.takewhile(isalpha, segment))
            prerelease = segment[len(prerelease_type)::]
            return prerelease_type, int(prerelease)
        if _is_int(components[2]):
            patch = int(components[2])
        else:
            # legacy version e.g. 1.2.0a1 (canonical is 1.2.0.0a1)
            # or 1.2.dev4.g1234 or 1.2.b4
            patch = 0
            components[2:2] = [0]
        remainder = components[3:]
        remainder_starts_with_int = False
        try:
            if remainder and int(remainder[0]):
                remainder_starts_with_int = True
        except ValueError:
            pass
        if remainder_starts_with_int:
            # old dev format - 0.1.2.3.g1234
            dev_count = int(remainder[0])
        else:
            if remainder and (remainder[0][0] == '0' or
                              remainder[0][0] in ('a', 'b', 'r')):
                # Current RC/beta layout
                prerelease_type, prerelease = _parse_type(remainder[0])
                remainder = remainder[1:]
            if remainder:
                component = remainder[0]
                if component.startswith('dev'):
                    dev_count = int(component[3:])
                elif component.startswith('g'):
                    # git hash - so use a dev_count of 1 as we have to have one
                    dev_count = 1
                    githash = component[1:]
                else:
                    raise ValueError(
                        'Unknown remainder %r in %r'
                        % (remainder, version_string))
        if len(remainder) > 1:
                githash = remainder[1][1:]
        return SemanticVersion(
            major, minor, patch, prerelease_type=prerelease_type,
            prerelease=prerelease, dev_count=dev_count, githash=githash)

    def brief_string(self):
        """Return the short version minus any alpha/beta tags."""
        return "%s.%s.%s" % (self._major, self._minor, self._patch)

    def debian_string(self):
        """Return the version number to use when building a debian package.

        This translates the PEP440/semver precedence rules into Debian version
        sorting operators.
        """
        return self._long_version("~", "+g")

    def decrement(self, minor=False, major=False):
        """Return a decremented SemanticVersion.

        Decrementing versions doesn't make a lot of sense - this method only
        exists to support rendering of pre-release versions strings into
        serialisations (such as rpm) with no sort-before operator.

        The 9999 magic version component is from the spec on this

        :return: A new SemanticVersion object.
        """
        if self._patch:
            new_patch = self._patch - 1
            new_minor = self._minor
            new_major = self._major
        else:
            new_patch = 9999
            if self._minor:
                new_minor = self._minor - 1
                new_major = self._major
            else:
                new_minor = 9999
                if self._major:
                    new_major = self._major - 1
                else:
                    new_major = 0
        return SemanticVersion(
            new_major, new_minor, new_patch)

    def increment(self, minor=False, major=False):
        """Return an incremented SemanticVersion.

        The default behaviour is to perform a patch level increment. When
        incrementing a prerelease version, the patch level is not changed
        - the prerelease serial is changed (e.g. beta 0 -> beta 1).

        Incrementing non-pre-release versions will not introduce pre-release
        versions - except when doing a patch incremental to a pre-release
        version the new version will only consist of major/minor/patch.

        :param minor: Increment the minor version.
        :param major: Increment the major version.
        :return: A new SemanticVersion object.
        """
        if minor is False:
            if os.environ.get('RELEASE_TYPE') == 'minor':
                minor = True
        if major is False:
            if os.environ.get('RELEASE_TYPE') == 'major':
                major = True
        
        if self._prerelease_type:
            new_prerelease_type = self._prerelease_type
            new_prerelease = self._prerelease + 1
            new_patch = self._patch
        else:
            new_prerelease_type = None
            new_prerelease = None
            new_patch = self._patch + 1
        if minor:
            new_minor = self._minor + 1
            new_patch = 0
            new_prerelease_type = None
            new_prerelease = None
        else:
            new_minor = self._minor
        if major:
            new_major = self._major + 1
            new_minor = 0
            new_patch = 0
            new_prerelease_type = None
            new_prerelease = None
        else:
            new_major = self._major
        return SemanticVersion(
            new_major, new_minor, new_patch,
            new_prerelease_type, new_prerelease)

    def _long_version(self, pre_separator, hash_separator, rc_marker=""):
        """Construct a long string version of this semver.

        :param pre_separator: What separator to use between components
            that sort before rather than after. If None, use . and lower the
            version number of the component to preserve sorting. (Used for
            rpm support)
        :param hash_separator: What separator to use to append the git hash.
        """
        if ((self._prerelease_type or self._dev_count)
                and pre_separator is None):
            segments = [self.decrement().brief_string()]
            pre_separator = "."
        else:
            segments = [self.brief_string()]
        if self._prerelease_type:
            segments.append(
                "%s%s%s%s" % (pre_separator, rc_marker, self._prerelease_type,
                              self._prerelease))
        if self._dev_count:
            segments.append(pre_separator)
            segments.append('dev')
            segments.append(self._dev_count)
            if self._githash:
                segments.append(hash_separator)
                segments.append(self._githash)
        return "".join(str(s) for s in segments)

    def release_string(self):
        """Return the full version of the package.

        This including suffixes indicating VCS status.
        """
        return self._long_version(".", ".g", "0")

    def rpm_string(self):
        """Return the version number to use when building an RPM package.

        This translates the PEP440/semver precedence rules into RPM version
        sorting operators. Because RPM has no sort-before operator (such as the
        ~ operator in dpkg),  we show all prerelease versions as being versions
        of the release before.
        """
        return self._long_version(None, "+g")

    def to_dev(self, dev_count, githash):
        """Return a development version of this semver.

        :param dev_count: The number of commits since the last release.
        :param githash: The git hash of the tree with this version.
        """
        return SemanticVersion(
            self._major, self._minor, self._patch, dev_count=dev_count,
            githash=githash)

    def to_release(self):
        """Discard any pre-release or dev metadata.

        :return: A new SemanticVersion with major/minor/patch the same as this
            one.
        """
        return SemanticVersion(self._major, self._minor, self._patch)

    def version_tuple(self):
        """Present the version as a version_info tuple.

        For documentation on version_info tuples see the Python
        documentation for sys.version_info.

        Since semver and PEP-440 represent overlapping but not subsets of
        versions, we have to have some heuristic / mapping rules:
         - a/b/rc take precedence.
         - if there is no pre-release version the dev version is used.
         - serial is taken from the dev/a/b/c component.
         - final non-dev versions never get serials.
        """
        segments = [self._major, self._minor, self._patch]
        if self._prerelease_type:
            type_map = {'a': 'alpha',
                        'b': 'beta',
                        'rc': 'candidate',
                        }
            segments.append(type_map[self._prerelease_type])
            segments.append(self._prerelease)
        elif self._dev_count:
            segments.append('dev')
            segments.append(self._dev_count - 1)
        else:
            segments.append('final')
            segments.append(0)
        return tuple(segments)


class Version(str):
    def __new__(self, package):

        result_string = VersionUtils.get_version(package)
        semantic_version = SemanticVersion.from_pip_string(result_string)
        
        if os.environ.get('RELEASE_TYPE', False) :
            version = str("{0}".format(semantic_version.brief_string()))
        else:
            version = str("{0}".format(semantic_version.release_string()))        
        
        obj = str.__new__(self, version)
        obj.package = package
        obj.semantic_version = semantic_version
        return obj

    def __repr__(self):
        """Include the name."""
        return "Version({0}:{1})".format(self.package, self)


__all__ = ['Version', 'VersionUtils']