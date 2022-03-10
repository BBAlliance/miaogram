import glob

from os.path import dirname, basename, isfile, join
from utils import logger

def imports(module):
    __import__(module, globals(), locals(), level=1)

imports("base")
logger.info("Controller initialing")

folder = dirname(__file__)
modules = [basename(f)[:-3] for f in glob.glob(join(folder, "*.py")) if isfile(f)]
modules = list(set(modules))
modules = [m for m in modules if not m.startswith(".") and not m.startswith("_") and m != "base"]

for module in modules:
    logger.info(f"Loading plugin: {module}")
    imports(module)
