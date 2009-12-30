'''
Providers: list of all input providers
'''

import pymt
import sys

from tuio import *
from mouse import *

if sys.platform == 'win32':
    from wm_touch import *
    from wm_pen import *

if sys.platform == 'darwin':
    try:
        from mactouch import *
    except:
        pymt.pymt_logger.exception('Input: MacMultitouchSupport is not available for your version')

