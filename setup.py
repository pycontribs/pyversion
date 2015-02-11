from setuptools import setup
from pbr import util
import version

os.environ['PBR_VERSION'] = version.__version__
setup(**util.cfg_to_args())
