import sys
from version.version3 import VersionUtils


def main(args):
    version = VersionUtils.get_version(args[0])
    if len(args) > 1 and args[1] == "increment":
        print(VersionUtils.increment(version))
    else:
        print(version)


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("usage: cli.py <package name>")
        print("returns the current version of the package name")
    else:
        main(sys.argv[1:])
