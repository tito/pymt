from pymt import *

css_add_file('reload.css')

b1 = MTButton(id='btn1', label='Reload CSS', pos=(100, 100))
b2 = MTButton(id='btn2', label='Button 2', pos=(250, 100))

@b1.event
def on_press(*largs):
    css_reload()

w = getWindow()
w.add_widget(b1)
w.add_widget(b2)

runTouchApp()
