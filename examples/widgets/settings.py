from __future__ import with_statement
from pymt import *

class MTTabs(MTWidget):
    def __init__(self, **kwargs):
        super(MTTabs, self).__init__(**kwargs)
        self.topbar = MTBoxLayout(orientation='horizontal')
        self.layout = MTBoxLayout(orientation='vertical')
        self.layout.add_widget(self.topbar)
        super(MTTabs, self).add_widget(self.layout)
        self.current = None
        self.tabs = dict()

    def add_widget(self, widget, tab=None):
        if tab is None:
            if not hasattr(widget, 'tab'):
                raise Exception('Widget added without tab information')
            else:
                tab = widget.tab
        button = MTButton(label=tab, size=(120, 40))
        button.tab_container = self
        @button.event
        def on_release(touchID, x, y):
            self.select(tab)
        self.topbar.add_widget(button)
        self.tabs[tab] = (button, widget)

    def select(self, tab):
        if tab not in self.tabs:
            return
        button, widget = self.tabs[tab]
        if self.current:
            self.layout.remove_widget(self.current, do_layout=False)
        self.layout.add_widget(widget, do_layout=False)
        self.current = widget
        self.layout.do_layout()

MTWidgetFactory.register('MTTabs', MTTabs)

xmlsettings = '''<?xml version="1.0" encoding="UTF-8"?>
<MTTabs>
    <MTForm tab="'General'"
        layout="factory.get('MTGridLayout')(spacing=20, cols=2, rows=2, uniform_height=True)">
        <MTFormLabel label="'Fullscreen'" halign="'right'"/>
        <MTFormCheckbox halign="'left'" id="'fs_fullscreen'"/>
        <MTFormLabel label="'Show FPS'" halign="'right'"/>
        <MTFormCheckbox halign="'left'" id="'fs_fps'"/>
    </MTForm>
    <MTForm tab="'Touches'"
        layout="factory.get('MTGridLayout')(spacing=20, cols=2, rows=2, uniform_height=True)">
        <MTFormLabel label="'Detection time'" halign="'right'"/>
        <MTFormInput halign="'left'" id="'fs_double_tap_time'"/>
        <MTFormLabel label="'Detection distance'" halign="'right'"/>
        <MTFormInput halign="'left'" id="'fs_double_tap_distance'"/>
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
fs_double_tap_time.value = pymt_config.get('pymt', 'double_tap_time')
fs_double_tap_distance.value = pymt_config.get('pymt', 'double_tap_distance')
fs_tuio_host.value = pymt_config.get('tuio', 'host')
fs_tuio_port.value = pymt_config.get('tuio', 'port')

# Do tabs
w.add_widget(xw)

#w.add_widget(MTPopup(width=300, content="Welcome to PyMT Widget Demonstration\nEnjoy this popup !"))
runTouchApp()
