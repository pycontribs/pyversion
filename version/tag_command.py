import os
import re
from distutils.core import Command
from distutils import log as logger
from .version import Version, VersionUtils

__all__ = ['tag']

class tag(Command):
    """ """
    description = "Will add a git tag corresponding to the version"
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

    def has_tag(self, tag_name=None, sha=None):
        """ """
        for tag in self.get_tags():
            if tag_name == tag:
                return True
        return False

    def run(self):
        """Will tag the currently active git commit id with the next release tag id"""
        sha = VersionUtils.run_git_command(['rev-parse', 'HEAD'], self.git_dir)
        tag = self.distribution.get_version()
        
        if self.has_tag(tag, sha):
            tags_sha = VersionUtils.run_git_command(['rev-parse', tag], self.git_dir)
            if sha != tags_sha:
                logger.error('git tag {0} sha does not match the sha requesting to be tagged, you need to increment the version number, Skipped Tagging!'.format(tag))
                return
            else:
                logger.info('git tag {0} already exists for this repo, Skipped Tagging!'.format(tag))
                return

        logger.info('Adding tag {0} for commit {1}'.format(tag, sha))
        if not self.dry_run:
            VersionUtils.run_git_command(['tag', '-m', '""', '--sign', tag, sha], self.git_dir, throw_on_error=True)
            logger.info('Pushing tag {0} to remote {1}'.format(tag, self.remote))
            VersionUtils.run_git_command(['push', self.remote, tag], self.git_dir, throw_on_error=True)
