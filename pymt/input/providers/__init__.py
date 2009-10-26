'''
Providers: list of all input providers
'''

import sys

from tuio import *
from mouse import *

if sys.platform == 'win32':
    from wm_touch import *
    from wm_pen import *
