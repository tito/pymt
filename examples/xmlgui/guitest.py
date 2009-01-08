from pymt import *


guixml = """<?xml version="1.0" encoding="UTF-8"?>
<Widget>
    <Button label="1" pos="(50,150)" color="(1,0,0)" />
    <Button label="2" pos="(250,150)" color="(0,1,0)" />
    <Button label="2" pos="(450,150)" color="(0,0,1)" />
    <Widget>
        <Button label="5" pos="(0,0)" color="(0,0,0)"/>
        <Button label="6" pos="(100,0)" color="(1,1,1)"/>
    </Widget>
</Widget>

"""



if __name__ == '__main__':

    w = UIWindow()
    widget = XMLWidget()
    widget.loadString(guixml)
    w.add_widget(widget)
    runTouchApp()