from pymt import *

m = MTWindow()

# create a simple popup
p = MTModalPopup(title='Hello World', content='I hope you will like it !')
m.add_widget(p)

runTouchApp()

