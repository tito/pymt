from pymt import *

widget = MTFlippableWidget()
widget.add_widget(MTLabel(label='Front'), side='front')
widget.add_widget(MTLabel(label='Back'), side='back')

@widget.event
def on_touch_down(touch):
    widget.flip()

runTouchApp(widget)
