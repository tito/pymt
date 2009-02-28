'''
You can use this file to test out your widgets or do live coding.
Click the grey box at the top left, this will popup a keyboard.
You can either use the displayed keyboard or your physical keyboard to type.
You can now add widgets by using the widgets dictionary :
    widgets['mywidget'] = MyWidget()
    w.add_widget(widgets['mywidget'])
Now you can interact with your widget :
    widgets['mywidget'].pos = (400,300)
    
There is also a quick way to add a widget, use the add function:
    add('slider', MTSlider())
    
Enjoy !

'''
from pymt import *

w = MTWindow()
widgets = {}
keyb = MTTextInput(size = (35,30), font_size = 16, pos = (0, w.height - 30))

def add(name, widget):
    widgets[name] = widget
    w.add_widget(widget)

@keyb.event
def on_text_validate():
    exec keyb.label
    keyb.label = ''
    keyb.size = (35,30)
    keyb.pos = (0, w.height - 30)

w.add_widget(keyb)

runTouchApp()