import os
import sys

from factories import *
from helpers import *

try:
    import colored_traceback.auto
    import colored_traceback.always
except ImportError:
    pass


sys.path.append(os.path.join(os.path.dirname(__name__), '..', 'src'))
