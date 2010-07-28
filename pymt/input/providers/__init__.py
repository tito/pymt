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
        pymt.pymt_logger.warning('Input: WM_Touch/WM_Pen is not supported by your version of Windows')

if sys.platform == 'darwin' or 'PYMT_DOC' in os.environ:
    try:
        from mactouch import *
    except:
        pymt.pymt_logger.exception('Input: MacMultitouchSupport is not supported by your system')

if sys.platform == 'linux2' or 'PYMT_DOC' in os.environ:
    try:
        from hidinput import *
    except:
        pymt.pymt_logger.exception('Input: HIDInput is not supported by your version of linux')
