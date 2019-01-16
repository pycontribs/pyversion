import os
import subprocess
import pkg_resources
from configparser import ConfigParser
from packaging.version import parse as parse_version
from packaging.version import LegacyVersion
from loguru import logger

try:
    import xmlrpclib
except ImportError:
    import xmlrpc.client as xmlrpclib


def version_keyword(dist, attr, value):
    """
    Implements the actual version setup() keyword.
    """
    if value == "PBR":
        from pbr.util import setup_cfg_to_setup_kwargs

        path = "setup.cfg"
        parser = ConfigParser()
        if not os.path.exists(path):
            raise ValueError("file '%s' does not exist" % os.path.abspath(path))
        parser.read(path)
        config = {}
        for section in parser.sections():
            config[section] = dict(parser.items(section))
        attrs = setup_cfg_to_setup_kwargs(config)
        version = str(Version(attrs["name"]))
        os.environ["PBR_VERSION"] = version
    else:
        version = str(Version(dist.metadata.get_name()))
    dist.metadata.version = version


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

        output = subprocess.Popen(
            cmd, stdout=out_location, stderr=err_location, env=newenv
        )
        out = output.communicate()
        if output.returncode and throw_on_error:
            raise Exception("%s returned %d" % (cmd, output.returncode))
        if len(out) == 0 or not out[0] or not out[0].strip():
            return ""
        return out[0].strip().decode("utf-8")

    @staticmethod
    def run_git_command(cmd, git_dir, **kwargs):
        if not isinstance(cmd, (list, tuple)):
            cmd = [cmd]
        return VersionUtils.run_shell_command(
            ["git", "--git-dir=%s" % git_dir] + cmd, **kwargs
        )

    @staticmethod
    def get_git_directory():
        return VersionUtils.run_shell_command(["git", "rev-parse", "--git-dir"])

    @staticmethod
    def git_is_installed():
        try:
            # We cannot use 'which git' as it may not be available
            # in some distributions, So just try 'git --version'
            # to see if we run into trouble
            VersionUtils.run_shell_command(["git", "--version"])
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
        except IndexError:
            return default_name, default
        except Exception as err:
            logger.exception(f"Unexpected exception: {err}")
            return default_name, default

    @staticmethod  # noqa: C901
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
        release_type = os.environ.get("RELEASE_TYPE", "micro")
        v = version._version
        # epoch
        epoch_name, epoch = VersionUtils.get_version_number(v, 0, None, "!")
        pre_name, pre = VersionUtils.get_version_number(v, 3, None, "pre")
        post_name, post = VersionUtils.get_version_number(v, 4, None, "post")
        dev_name, dev = VersionUtils.get_version_number(v, 2, None, "dev")
        _, major = VersionUtils.get_version_number(v[1], 0, 0)
        _, minor = VersionUtils.get_version_number(v[1], 1, None)
        _, micro = VersionUtils.get_version_number(v[1], 2, None)

        # Handle dev/pre/post
        if release_type == "pre":
            micro, post, pre = VersionUtils.process_pre(micro, post, pre)

        if release_type == "post":
            dev, post = VersionUtils.process_post(dev, post)

        if release_type == "dev":
            dev = VersionUtils.process_dev(dev)

        if release_type == "micro":
            dev, micro, minor, post, pre = VersionUtils.process_micro(
                dev, micro, minor, post, pre
            )

        if release_type == "minor":
            dev, micro, minor, post, pre = VersionUtils.process_minor(
                dev, micro, minor, post, pre
            )

        if release_type == "major":
            dev, major, micro, minor, post, pre = VersionUtils.process_major(
                dev, major, micro, minor, post, pre
            )

        # Handle Epoch
        if release_type == "epoch":
            dev, epoch, major, micro, minor, post, pre = VersionUtils.process_epoch(
                dev, epoch, major, micro, minor, post, pre
            )

        local = "".join(v[5] or []) or None

        version_list = [major, minor, micro]
        if release_type not in ["epoch", "major", "minor", "micro", "pre"]:
            version_list += list(v[1][3:])
        version_string = ".".join([str(x) for x in version_list if x or x == 0])

        if epoch:
            version_string = str(epoch) + epoch_name + version_string
        if pre is not None:
            version_string = VersionUtils.calc_pre_version_string(
                pre, pre_name, version_string
            )
        if post is not None:
            version_string += "." + post_name + str(post)
        if dev is not None:
            version_string += "." + dev_name + str(dev)
        if local is not None:
            version_string += "." + str(local)

        return version_string

    @staticmethod
    def calc_pre_version_string(pre, pre_name, version_string):
        if pre_name == "pre":
            version_string += "."
        version_string += pre_name
        if pre:
            version_string += str(pre)
        return version_string

    @staticmethod
    def process_epoch(dev, epoch, major, micro, minor, post, pre):
        epoch += 1
        major = 1
        minor = 0
        micro = 0
        dev = None
        pre = None
        post = None
        return dev, epoch, major, micro, minor, post, pre

    @staticmethod
    def process_major(dev, major, micro, minor, post, pre):
        major += 1
        if minor is not None:
            minor = 0
        if micro is not None:
            micro = 0
        dev = None
        pre = None
        post = None
        return dev, major, micro, minor, post, pre

    @staticmethod
    def process_minor(dev, micro, minor, post, pre):
        if minor is None:
            minor = 1
        else:
            minor += 1
        if micro is not None:
            micro = 0
        dev = None
        pre = None
        post = None
        return dev, micro, minor, post, pre

    @staticmethod
    def process_micro(dev, micro, minor, post, pre):
        if micro is None:
            if minor is None:
                minor = 0
            micro = 1
        elif pre is None:
            micro += 1
        dev = None
        pre = None
        post = None
        return dev, micro, minor, post, pre

    @staticmethod
    def process_dev(dev):
        if dev is None:
            dev = 1
        else:
            dev += 1
        return dev

    @staticmethod
    def process_post(dev, post):
        if post is None:
            post = 1
        else:
            post += 1
        if dev:
            dev = None
        return dev, post

    @staticmethod
    def process_pre(micro, post, pre):
        if pre is None:
            pre = 1
            micro += 1
        else:
            pre += 1
        if post:
            post = None
        return micro, post, pre

    @staticmethod
    def get_version_from_pkg_resources(package):
        try:
            requirement = pkg_resources.Requirement.parse(package)
            provider = pkg_resources.get_provider(requirement)
            return provider.version
        except Exception as err:
            print(f"get_version_from_pkg_resources: {err}")
            return None

    @staticmethod
    def get_version_from_pip(package):
        try:
            versions = eval(f"{package}.__version__")
        except Exception:
            versions = None

        if versions is None:
            try:

                def get_ver(pkg):
                    pkg = pkg.lower()
                    return next(
                        (
                            p.version
                            for p in pkg_resources.working_set
                            if p.project_name.lower() == pkg
                        ),
                        None,
                    )

                versions = get_ver(package)
            except Exception as err:
                logger.exception(f"get_version() failed:{err}")
                versions = None
        return versions

    @staticmethod
    def get_version_from_pypi(package):
        try:
            with xmlrpclib.ServerProxy("https://pypi.python.org/pypi") as client:
                versions = client.package_releases(package)
                if len(versions) >= 1:
                    return versions[0]
                else:
                    return None
        except Exception as err:
            logger.exception(f"get_version_from_pypi: {err}")
            return None

    @staticmethod
    def get_version(package):
        version = VersionUtils.get_version_from_pip(package)
        if not version:
            version = VersionUtils.get_version_from_pkg_resources(package)
        if not version:
            version = VersionUtils.get_version_from_pypi(package)
        # probably could add a few more methods here to try
        if not version:
            version = "0.0.1"
        version = parse_version(version)
        return version


class Version(str):
    """Proxy for the pip packaging version class"""

    def __new__(cls, package):
        return VersionUtils.get_version(package)
