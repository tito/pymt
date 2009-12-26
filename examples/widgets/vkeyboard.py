# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Virtual Keyboard Demo'
PLUGIN_AUTHOR = 'Thomas Hansen'
PLUGIN_DESCRIPTION = 'This example shows how to use a virtual keyboard widget which is present int pymt core'

from pymt import *

if __name__ == "__main__":
    w = MTWindow()
    text_input = MTTextInput()
    w.add_widget(text_input)
    runTouchApp()
