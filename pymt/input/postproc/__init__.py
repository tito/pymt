'''
Input Postproc: analyse and process input (double tap, ignore list...)
'''

__all__ = ['pymt_postproc_modules']

import os
import doubletap
import ignorelist
import retaintouch

pymt_postproc_modules = []

# Don't go further if we generate documentation
if 'PYMT_DOC' not in os.environ:
    pymt_postproc_modules.append(retaintouch.InputPostprocRetainTouch())
    pymt_postproc_modules.append(ignorelist.InputPostprocIgnoreList())
    pymt_postproc_modules.append(doubletap.InputPostprocDoubleTap())
