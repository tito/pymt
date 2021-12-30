'''
Input Postproc: analyse and process input (double tap, ignore list...)
'''

__all__ = ('pymt_postproc_modules', )

import os
from . import doubletap
from . import ignorelist
from . import retaintouch
from . import dejitter

# Mapping of ID to module
pymt_postproc_modules = {}

# Don't go further if we generate documentation
if 'PYMT_DOC' not in os.environ:
    pymt_postproc_modules['retaintouch'] = retaintouch.InputPostprocRetainTouch()
    pymt_postproc_modules['ignorelist'] = ignorelist.InputPostprocIgnoreList()
    pymt_postproc_modules['doubletap'] = doubletap.InputPostprocDoubleTap()
    pymt_postproc_modules['dejitter'] = dejitter.InputPostprocDejitter()
