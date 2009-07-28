'''
Input Postproc: analyse and process input (double tap, ignore list...)
'''

__all__ = ['pymt_postproc_modules']

import doubletap
import ignorelist

pymt_postproc_modules = [
    ignorelist.InputPostprocIgnoreList(),
    doubletap.InputPostprocDoubleTap(),
]
