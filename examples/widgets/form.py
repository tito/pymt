from __future__ import with_statement
from pymt import *

xmldef = '''<?xml version="1.0" encoding="UTF-8"?>
<MTScatterPlane>
    <MTForm pos="(200,200)"
    layout="factory.get('MTGridLayout')(spacing=20, cols=2, rows=5, uniform_height=True)">
        <MTFormLabel label="'Name'" halign="'right'"/>
        <MTFormInput id="'input_name'"/>
        <MTFormLabel label="'Surname'" halign="'right'"/>
        <MTFormInput id="'input_surname'"/>
        <MTFormLabel label="'Nickname'" halign="'right'"/>
        <MTFormInput id="'input_nickname'"/>
        <MTFormLabel label="'Age'" halign="'right'"/>
        <MTFormInput id="'input_age'"/>
        <MTFormButton label="'Send'"/>
        <MTFormButton label="'Cancel'"/>
    </MTForm>
</MTScatterPlane>
'''

w = MTWindow()
w.add_widget(XMLWidget(xml=xmldef))
w.add_widget(MTPopup(width=300, content="Welcome to PyMT Widget Demonstration\nEnjoy this popup !"))
runTouchApp()
