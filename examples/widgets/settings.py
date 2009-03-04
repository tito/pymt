from __future__ import with_statement
from pymt import *

xmldef = '''<?xml version="1.0" encoding="UTF-8"?>
<MTForm pos="(0,0)"
layout="factory.get('MTGridLayout')(spacing=20, cols=2, rows=7, uniform_height=True)">
    <MTFormLabel label="'Fullscreen'" halign="'right'"/>
    <MTFormCheckbox halign="'left'" id="'chk_fullscreen'"/>
    <MTFormLabel label="'Show FPS'" halign="'right'"/>
    <MTFormCheckbox halign="'left'" id="'chk_fps'"/>
    <MTFormButton label="'Save'"/>
    <MTFormButton label="'Close'"/>
</MTForm>
'''

class MTTabs(MTWidget):
    def __init__(self, **kwargs):
        super(MTTabs, self).__init__(**kwargs)
        self.topbar = MTBoxLayout(orientation='horizontal')
        self.layout = MTBoxLayout(orientation='vertical')
        self.layout.add_widget(self.topbar)
        super(MTTabs, self).add_widget(self.layout)
        self.current = None
        self.tabs = dict()

    def add_widget(self, widget, title):
        button = MTButton(label=title, size=(120, 40))
        button.tab_container = self
        @button.event
        def on_release(touchID, x, y):
            self.select(title)
        self.topbar.add_widget(button)
        self.tabs[title] = (button, widget)

    def select(self, title):
        if title not in self.tabs:
            return
        button, widget = self.tabs[title]
        if self.current:
            self.layout.remove_widget(self.current, do_layout=False)
        self.layout.add_widget(widget, do_layout=False)
        self.current = widget
        self.layout.do_layout()



w = MTWindow()

def action_fullscreen(checked):
    global w
    w.set_fullscreen(checked)

def action_fps(checked):
    global w
    w.show_fps = checked

xw = XMLWidget(xml=xmldef).children[0]
chk_fullscreen = getWidgetById('chk_fullscreen')
chk_fullscreen.push_handlers(on_check=action_fullscreen)
chk_fps = getWidgetById('chk_fullscreen')
chk_fps.push_handlers(on_check=action_fps)

m = MTTabs()
m.add_widget(xw, 'Form')
m.add_widget(MTTextInput(), 'Text input')
m.add_widget(MTButton(label='plop'), 'Button')
p = MTScatterPlane()
p.add_widget(m)
w.add_widget(p)

#w.add_widget(MTPopup(width=300, content="Welcome to PyMT Widget Demonstration\nEnjoy this popup !"))
runTouchApp()
