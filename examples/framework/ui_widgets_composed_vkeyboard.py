from pymt import *
keyboard = MTVKeyboard()

@keyboard.event
def on_key_down(*largs):
    print 'key down:', largs

@keyboard.event
def on_key_up(*largs):
    print 'key up:', largs

@keyboard.event
def on_text_change(*largs):
    print 'text change', largs

runTouchApp(keyboard)
