from pymt import *

#some basic widgets
slider = MTSlider(orientation="horizontal")
button = MTButton(label="Reset")
label  = MTLabel(label="Label Text", font_size=20)

#some event handling using connect
slider.connect("on_value_change", label, "label")

#some event handling using custom event handler function
def reset(*args):
   label.label = "Label Text"
button.push_handlers(on_press=reset)

#create a root wodget and add our example widgets to it
root = MTBoxLayout(orientation="vertical")
root.add_widgets(slider, button, label)

#run the application
runTouchApp(root)
