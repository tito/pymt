'''
Input Postproc: analyse and process input (double tap, ignore list...)
'''

__all__ = ['pymt_postproc_modules']

import os
import sys
import doubletap
import ignorelist

pymt_postproc_modules = []

# Don't go further if we generate documentation
if os.path.basename(sys.argv[0]) not in ('sphinx-build', 'autobuild.py'):
    pymt_postproc_modules.append(ignorelist.InputPostprocIgnoreList())
    pymt_postproc_modules.append(doubletap.InputPostprocDoubleTap())
