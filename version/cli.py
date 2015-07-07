import sys
from version import VersionUtils


def main():
    args = sys.argv[1:]
    version = VersionUtils.get_version(args[0])
    if len(args) > 1 and args[1] == 'increment':
        print VersionUtils.increment(version)
    else:
        print version

if __name__ == "__main__":
    main()
