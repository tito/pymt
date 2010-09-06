from pymt import *

guixml = '''<?xml version="1.0" encoding="UTF-8"?>
<MTWidget>
    <MTButton label="1" pos="(50,150)" color="(1,0,0)" />
    <MTButton label="2" pos="(250,150)" color="(0,1,0)" />
    <MTButton label="2" pos="(450,150)" color="(0,0,1)" />
    <MTWidget>
        <MTButton label="5" pos="(0,0)" color="(0,0,0)"/>
        <MTButton label="6" pos="(100,0)" color="(1,1,1)"/>
    </MTWidget>
</MTWidget>
'''

# create the gui from xml
widget = XMLWidget(xml=guixml)

# run the app from the root widget
runTouchApp(widget.root)

