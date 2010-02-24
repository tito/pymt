'''
You can use this file to test out your widgets or do live coding.
Click the grey box at the top left, this will popup a keyboard. (you can hit the tab key also)
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
history = []
count = -1

def on_key_press(symbol, modifiers):
    global count
    if symbol == 65362: #up arrow
        if not keyb.is_active_input:
           keyb.show_keyboard()
        count = count + 1
        if count == len(history):
            count = len(history) - 1
        keyb.label = list(reversed(history))[count]

    if symbol == 65364: #down arrow
        if not keyb.is_active_input:
           keyb.show_keyboard()
        if count != -1:
            count = count - 1
        if count == -1:
            count = -1
            keyb.label = ''
            return
        keyb.label = list(reversed(history))[count]



    if symbol == 65289: #tab
        if not keyb.is_active_input:
           keyb.show_keyboard()
        else: keyb.hide_keyboard()
w.push_handlers(on_key_press = on_key_press)

keyb = MTTextInput(size = (35,30), font_size = 16, pos = (0, w.height - 30))

def add(name, widget):
    widgets[name] = widget
    w.add_widget(widget)

@keyb.event
def on_text_validate():
    global count
    count = -1
    try:
        exec keyb.label
    except Exception, e:
        print 'Error', e
        p = MTModalPopup(title='Exception occured', content=str(e))
        w.add_widget(p)
    history.append(keyb.label)
    keyb.label = ''
    keyb.size = (35,30)
    keyb.pos = (0, w.height - 30)

w.add_widget(keyb)

runTouchApp()
