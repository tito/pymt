# Text area (multiline text input)
from pymt import *

wid = MTTextArea()

@wid.event
def on_text_validate():
    print 'Text have been validated:', wid.value

@wid.event
def on_text_change(text):
    print 'Text have been changed (not validated):', text

runTouchApp(wid)

