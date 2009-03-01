from pymt import *

mms = MTWindow()

s = MTScatterWidget(size=(200, 200), pos=(400, 300))
mms.add_widget(s)

l = MTLabel(text='Hello!', pos=(40, 40))
s.add_widget(l, side='back')

b = MTButton(label='flip', size=(100, 100), pos=(100, 100))
s.add_widget(b, side='front')
s.add_widget(b, side='back')

f = MTVectorSlider(radius=40, pos=(40, 40))
s.add_widget(f, side='front')

@b.event
def on_press(touchID, x, y):
    s.flip()

runTouchApp()
