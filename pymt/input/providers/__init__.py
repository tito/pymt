'''
Providers: list of all input providers
'''

import pymt
import sys
import os

from pymt.input.providers.tuio import *
from pymt.input.providers.mouse import *

if sys.platform == 'win32' or 'PYMT_DOC' in os.environ:
    try:
        from pymt.input.providers.wm_touch import *
        from pymt.input.providers.wm_pen import *
    except:
        pymt.pymt_logger.warning('Input: WM_Touch/WM_Pen is not supported by your version of Windows')

if sys.platform == 'darwin' or 'PYMT_DOC' in os.environ:
    try:
        from pymt.input.providers.mactouch import *
    except:
        pymt.pymt_logger.exception('Input: MacMultitouchSupport is not supported by your system')

if sys.platform == 'linux2' or 'PYMT_DOC' in os.environ:
    try:
        from pymt.input.providers.probesysfs import *
    except:
        pymt.pymt_logger.exception('Input: ProbeSysfs is not supported by your version of linux')
    try:
        from pymt.input.providers.mtdev import *
    except:
        pymt.pymt_logger.exception('Input: MTDev is not supported by your version of linux')
    try:
        from pymt.input.providers.hidinput import *
    except:
        pymt.pymt_logger.exception('Input: HIDInput is not supported by your version of linux')
