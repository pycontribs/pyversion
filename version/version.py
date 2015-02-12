import os
import subprocess
from pip._vendor import pkg_resources
from pip._vendor.packaging.version import parse as parse_version
from pip._vendor.packaging.version import LegacyVersion

try:
    import xmlrpclib
except ImportError:
    import xmlrpc.client as xmlrpclib

class VersionUtils(object):
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
    def get_version_number(version_tuple, index=None, default=None, default_name=None):
        try:
            rv = version_tuple[index]
            if isinstance(rv, tuple):
                return rv
            else:
                return default_name, rv
        except:
            return default_name, default
    
    @staticmethod
    def increment(version):
        """Return an incremented version string."""
        release_version = os.environ.get("RELEASE_VERSION", None)
        if release_version is not None:
            return release_version
        if isinstance(version, LegacyVersion):
            msg = """{0} is considered a legacy version and does not
            support automatic incrementing.  Please bring your version
            numbering into PEP440 standards and then it can be
            automatically incremented.
            """
            raise Exception(msg.format(version))
        release_type = os.environ.get('RELEASE_TYPE', 'micro')
        v = version._version
        first_pre_release = False
        # epoch
        epoch_name, epoch = VersionUtils.get_version_number(v, 0, None, '!')
        pre_name, pre = VersionUtils.get_version_number(v, 3, None, 'pre')
        post_name, post = VersionUtils.get_version_number(v, 4, None, 'post')
        dev_name, dev = VersionUtils.get_version_number(v, 2, None, 'dev')
        _, major = VersionUtils.get_version_number(v[1], 0, 0)
        _, minor = VersionUtils.get_version_number(v[1], 1, None)
        _, micro = VersionUtils.get_version_number(v[1], 2, None)
        
        # Handle dev/pre/post
        if release_type == 'pre':
            if pre is None:
                pre = 1
                micro += 1
            else:
                pre += 1
            if post:
                post = None

        if release_type == 'post':
            if post is None:
                post = 1
            else:
                post += 1
            if dev:
                dev = None
        
        if release_type == 'dev':
            if dev is None:
                dev = 1
            else:
                dev += 1
        
        if release_type == 'micro':
            if micro is None:
                if minor is None:
                    minor = 0
                micro = 1
            elif pre is None:
                micro += 1
            dev = None
            pre = None
            post = None

        if release_type == 'minor':
            if minor is None:
                minor = 1
            else:
                minor += 1
            if micro is not None:
                micro = 0
            dev = None
            pre = None
            post = None

        if release_type == 'major':
            major += 1
            if minor is not None:
                minor = 0
            if micro is not None:
                micro = 0
            dev = None
            pre = None
            post = None

        # Handle Epoch
        if release_type == 'epoch':
            epoch += 1
            major = 1
            minor = 0
            micro = 0
            dev = None
            pre = None
            post = None
        
        local = "".join(v[5] or []) or None
        
        version_list = [major, minor, micro]
        if release_type not in ['epoch', 'major', 'minor', 'micro', 'pre']:
            version_list += list(v[1][3:])
        version_string = ".".join([str(x) for x in version_list if x or x == 0])
        
        if epoch:
            version_string = str(epoch) + epoch_name + version_string
        if pre is not None:
            if pre_name == 'pre':
                version_string += '.'
            version_string +=  pre_name
            if pre:
                version_string += str(pre)
        if post is not None:
            version_string += '.' + post_name + str(post)    
        if dev is not None:
            version_string += '.' + dev_name + str(dev)
        if local is not None:
            version_string += '.' + str(local)


        return version_string
    
    @staticmethod
    def get_version_from_pkg_resources(package):
        try:
            requirement = pkg_resources.Requirement.parse(package)
            provider = pkg_resources.get_provider(requirement)
            return provider.version
        except:
            return None
        
    @staticmethod
    def get_version_from_pip(package):
        # this should handle getting package versions from any pip configured index
        return None
        
    @staticmethod
    def get_version_from_pypi(package):
        try:
            client = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')
            versions = client.package_releases(package)
            if len(versions) >= 1:
                return versions[0]
            else:
                return None
        except:
            return None
    
    @staticmethod
    def get_version(package):
        version = VersionUtils.get_version_from_pkg_resources(package)
        if not version:
            version = VersionUtils.get_version_from_pip(package)
        if not version:
            version = VersionUtils.get_version_from_pypi(package)
        # probably could add a few more methods here to try
        if not version:
            version = "0.0.1"            
        version = parse_version(version)
        return version
        

class Version(str):
    '''Proxy for the pip packaging version class'''
    def __new__(self, package):
        return VersionUtils.get_version(package)
