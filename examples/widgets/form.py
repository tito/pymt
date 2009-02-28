from __future__ import with_statement
from pymt import *

xmldef = '''<?xml version="1.0" encoding="UTF-8"?>
<MTScatterPlane>
    <MTForm pos="(200,200)"
    layout="factory.get('MTGridLayout')(spacing=20, cols=2, rows=7, uniform_height=True)">
        <MTFormLabel label="'Fullscreen'" halign="'right'"/>
        <MTFormCheckbox halign="'left'" id="'chk_fullscreen'"/>
        <MTFormLabel label="'Show FPS'" halign="'right'"/>
        <MTFormCheckbox halign="'left'" id="'chk_fps'"/>
        <MTFormButton label="'Save'"/>
        <MTFormButton label="'Close'"/>
    </MTForm>
</MTScatterPlane>
'''

w = MTWindow()

def action_fullscreen(checked):
    global w
    w.set_fullscreen(checked)

def action_fps(checked):
    global w
    w.show_fps = checked


w.add_widget(XMLWidget(xml=xmldef))

chk_fullscreen = getWidgetById('chk_fullscreen')
chk_fullscreen.push_handlers(on_check=action_fullscreen)
chk_fps = getWidgetById('chk_fullscreen')
chk_fps.push_handlers(on_check=action_fps)


#w.add_widget(MTPopup(width=300, content="Welcome to PyMT Widget Demonstration\nEnjoy this popup !"))
runTouchApp()
