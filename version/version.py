import os
from pip._vendor import pkg_resources
from pip._vendor.packaging.version import parse as parse_version
from pip._vendor.packaging.version import LegacyVersion

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
    def increment(version):
        """Return an incremented version string."""
        if isinstance(version, LegacyVersion):
            msg = """{0} is considered a legacy version and does not
            support automatic incrementing.  Please bring your version
            numbering into PEP440 standards and then it can be
            automatically incremented.
            """
            raise Exception(msg.format(version))
        release_type = os.environ.get('RELEASE_TYPE', 'micro')
        v = version._version
        
        # Handle Pre/Post
        if release_type == 'dev':
            if v[2] is None:
                dev = "dev1"
            else:
                dev = "dev{0}".format(v[2][1] + 1)
        else:
            dev = None
        if release_type == 'pre':
            if v[2] is None:
                pre = "pre1"
            else:
                pre = "pre{0}".format(v[2][1] + 1)
        else:
            pre = None
        if release_type == 'post':
            if v[2] is None:
                post = "post1"
            else:
                post = "post{0}".format(v[2][1] + 1)
            dev
        else:
            post = None
                
        # Handle Release
        if release_type == 'micro':
            micro = v[1][2] + 1
            dev = None
            pre = None
            post = None
        else:
            micro = v[1][2]
        if release_type == 'minor':
            minor = v[1][1] + 1
            micro = 0
            dev = None
            pre = None
            post = None
        else:
            minor = v[1][1]
        if release_type == 'major':
            major = v[1][0] + 1
            minor = 0
            micro = 0
            dev = None
            pre = None
            post = None
        else:
            major = v[1][0]
            
        # Handle Epoch
        if release_type == 'epoch':
            epoch = "{0}!".format(v[0] + 1)
            major = 1
            minor = 0
            micro = 0
            dev = None
            pre = None
            post = None
        else:
            epoch = None
        
        local = "".join(v[5] or []) or None
        
        if release_type in ['epoch', 'major', 'minor', 'micro']:
            version_list = release = [epoch, major, minor, micro] + [dev, pre, post, local]
        else:
            version_list = release = [epoch, major, minor, micro] + list(v[1][3:]) + [dev, pre, post, local]
        version_string = ".".join([str(x) for x in version_list if x or x == 0])
        return version_string
    
    @staticmethod
    def get_version(package):
        version = os.environ.get("RELEASE_VERSION", None)
        if not version:
            try:
                requirement = pkg_resources.Requirement.parse(package)
                provider = pkg_resources.get_provider(requirement)
                version = provider.version
            except:
                version = "0.0.1"
        version = parse_version(version)
        return version
        

class Version(str):
    '''Proxy for the pip packaging version class'''
    def __new__(self, package):
        return VersionUtils.get_version(package)
