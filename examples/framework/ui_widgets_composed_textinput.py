# Text input widget with a switch to use hardware keyboard or not
from pymt import *

wid = MTTextInput()

@wid.event
def on_text_change(text):
    print 'Text have been changed (not validated):', text

runTouchApp(wid)
