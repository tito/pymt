from __future__ import with_statement
from pymt import *

xmlsettings = '''<?xml version="1.0" encoding="UTF-8"?>
<MTTabs pos="(0,480)">
    <MTForm tab="'General'"
        layout="factory.get('MTGridLayout')(spacing=20, cols=2, rows=4, uniform_height=True)">
        <MTFormLabel label="'Fullscreen'" halign="'right'"/>
        <MTFormCheckbox halign="'left'" id="'fs_fullscreen'"/>
        <MTFormLabel label="'Show FPS'" halign="'right'"/>
        <MTFormCheckbox halign="'left'" id="'fs_fps'"/>
        <MTFormLabel label="'Double Tap time'" halign="'right'"/>
        <MTFormSlider min="0" max="1000" id="'fs_double_tap_time'"/>
        <MTFormLabel label="'Double Tap distance'" halign="'right'"/>
        <MTFormSlider min="0" max="1000" id="'fs_double_tap_distance'"/>
    </MTForm>
    <MTForm tab="'Tuio'"
        layout="factory.get('MTGridLayout')(spacing=20, cols=2, rows=2, uniform_height=True)">
        <MTFormLabel label="'Host'" halign="'right'"/>
        <MTFormInput halign="'left'" id="'fs_tuio_host'"/>
        <MTFormLabel label="'Port'" halign="'right'"/>
        <MTFormInput halign="'left'" id="'fs_tuio_port'"/>
    </MTForm>
</MTTabs>
'''

w = MTWindow()

def action_fullscreen(checked):
    global w
    w.set_fullscreen(checked)

def action_fps(checked):
    global w
    w.show_fps = checked

xw = XMLWidget(xml=xmlsettings).children[0]

# Connect
fs_fullscreen = getWidgetById('fs_fullscreen')
fs_fullscreen.push_handlers(on_check=action_fullscreen)
fs_fps = getWidgetById('fs_fps')
fs_fps.push_handlers(on_check=action_fps)
fs_double_tap_time = getWidgetById('fs_double_tap_time')
fs_double_tap_distance = getWidgetById('fs_double_tap_distance')
fs_tuio_host = getWidgetById('fs_tuio_host')
fs_tuio_port = getWidgetById('fs_tuio_port')

# Set default values
fs_fullscreen.checked = pymt_config.getboolean('pymt', 'fullscreen')
fs_fps.checked = pymt_config.getboolean('pymt', 'show_fps')
fs_double_tap_time.value = pymt_config.getint('pymt', 'double_tap_time')
fs_double_tap_distance.value = pymt_config.get('pymt', 'double_tap_distance')
fs_tuio_host.value = pymt_config.get('tuio', 'host')
fs_tuio_port.value = pymt_config.get('tuio', 'port')

# Do tabs
w.add_widget(xw)

#w.add_widget(MTPopup(width=300, content="Welcome to PyMT Widget Demonstration\nEnjoy this popup !"))
runTouchApp()
