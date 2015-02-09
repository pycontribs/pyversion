import os
import re
from distutils.core import Command
from distutils import log as logger
from .version import Version, SemanticVersion, VersionUtils

__all__ = ['tag']

VERSION_MATCH = re.compile('^(?P<major>\d\d*)\.(?P<minor>\d*)\.(?P<patch>\d*)($|\.|)(?P<pre_release>[0-9A-Za-z-]*)($|\.g|)(?P<git_id>[0-9A-Za-z-]*)($|\+)(?P<metadata>[0-9A-Za-z-\.]*$)')


class tag(Command):
    """ """
    description = "Will add a git tag for the highest defined version increment based on the current version detected"
    user_options = [('remote=', 'r', "Git Remote Name (default: origin)")]

    def initialize_options(self):
        self.remote = os.environ.get('GIT_REMOTE', 'origin')

    def finalize_options(self):
        """ """
        if not VersionUtils.git_is_installed():
            raise Exception('Unable to run git commandline, please make sure git is installed!')
        self.git_dir = VersionUtils.get_git_directory()

    def get_tags(self):
        """ """
        tags = VersionUtils.run_git_command(['tag'], self.git_dir)
        return sorted(tags.splitlines())

    def has_tag(self, tag_name=None):
        """ """
        for tag in self.get_tags():
            if tag_name == tag:
                return True
        return False

    def increment(self, sem_ver):
        """Return an incremented SemanticVersion."""
        if os.environ.get('RELEASE_TYPE') == 'minor':
            minor = True
        if os.environ.get('RELEASE_TYPE') == 'major':
            major = True

        if sem_ver._prerelease_type:
            new_prerelease_type = sem_ver._prerelease_type
            new_prerelease = sem_ver._prerelease + 1
            new_patch = sem_ver._patch
        else:
            new_prerelease_type = None
            new_prerelease = None
            new_patch = sem_ver._patch + 1
        if minor:
            new_minor = sem_ver._minor + 1
            new_patch = 0
            new_prerelease_type = None
            new_prerelease = None
        else:
            new_minor = sem_ver._minor
        if major:
            new_major = sem_ver._major + 1
            new_minor = 0
            new_patch = 0
            new_prerelease_type = None
            new_prerelease = None
        else:
            new_major = sem_ver._major
        return SemanticVersion(
            new_major, new_minor, new_patch,
            new_prerelease_type, new_prerelease)

    def run(self):
        """Will tag the currently active git commit id with the next release tag id"""
        sha = VersionUtils.run_git_command(['rev-parse', 'HEAD'], self.git_dir)
        version = os.environ.get("RELEASE_VERSION", None)
        if not Version:
            version = Version(self.distribution.get_name())
        tag = self.increment(version.semantic_version).release_string()
        
        if self.has_tag(tag):
            logger.info('git tag {0} already exists for this repo, Skipping.'.format(tag))
        else:
            logger.info('Adding tag {0} for commit {1}'.format(tag, sha))
            if not self.dry_run:
                VersionUtils.run_git_command(['tag', '-m', '""', '--sign', tag, sha], self.git_dir, throw_on_error=True)
                logger.info('Pushing tag {0} to remote {1}'.format(tag, self.remote))
                VersionUtils.run_git_command(['push', self.remote, tag], self.git_dir, throw_on_error=True)
