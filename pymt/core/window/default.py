'''
Default: create the default window if not exist
'''

from pymt.base import getWindow

if getWindow() is None:
    from pymt.core.window import Window
    from pymt import pymt_configure
    Window()
    pymt_configure
