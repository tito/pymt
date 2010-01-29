'''
Providers: list of all input providers
'''

import pymt
import sys
import os

from tuio import *
from mouse import *

if sys.platform == 'win32' or 'PYMT_DOC' in os.environ:
    try:
        from wm_touch import *
        from wm_pen import *
    except:
        pymt.pymt_logger.warning('Input: WM_Touch/WM_Pen is not available for your window version')

if sys.platform == 'darwin' or 'PYMT_DOC' in os.environ:
    try:
        from mactouch import *
    except:
        pymt.pymt_logger.exception('Input: MacMultitouchSupport is not available for your version')

