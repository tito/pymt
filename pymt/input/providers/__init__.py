'''
Providers: list of all input providers
'''

import sys
import os

from pymt.logger import Logger
from pymt.input.providers.tuio import *
from pymt.input.providers.mouse import *

if sys.platform == 'win32' or 'PYMT_DOC' in os.environ:
    try:
        from pymt.input.providers.wm_touch import *
        from pymt.input.providers.wm_pen import *
    except:
        Logger.warning('Input: WM_Touch/WM_Pen is not supported by your version of Windows')

if sys.platform == 'darwin' or 'PYMT_DOC' in os.environ:
    try:
        from pymt.input.providers.mactouch import *
    except:
        Logger.exception('Input: MacMultitouchSupport is not supported by your system')

if sys.platform == 'linux2' or 'PYMT_DOC' in os.environ:
    try:
        from pymt.input.providers.probesysfs import *
    except:
        Logger.exception('Input: ProbeSysfs is not supported by your version of linux')
    try:
        from pymt.input.providers.mtdev import *
    except:
        Logger.exception('Input: MTDev is not supported by your version of linux')
    try:
        from pymt.input.providers.hidinput import *
    except:
        Logger.exception('Input: HIDInput is not supported by your version of linux')
    try:
        from pymt.input.providers.linuxwacom import *
    except:
        Logger.exception('Input: LinuxWacom is not supported by your version of linux')
