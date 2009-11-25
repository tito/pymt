from pymt import *
from serializer import Serializer

# Create a widget tree
box = MTBoxLayout()
box.add_widget(MTSlider(max=2000, value=500))
box.add_widget(MTSlider(value=75, orientation='horizontal'))
#box.add_widget(MTButton(label='hello'))
#box.add_widget(MTScatterWidget())
#box = MTScatterWidget()

# Serialize the tree
data = Serializer()
xml = data.serialize(box)

# Unserialize the tree
data = Serializer()
box = data.unserialize(xml)

# Run touch app from unserialized tree
runTouchApp(box)

