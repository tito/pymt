from pymt import *

w = MTWindow()

cm = MTCircularSlider(pos=(w.width/2-200,w.height/2),radius=300,thickness=100,padding=5,sweep_angle=130,rotation=-60,min=0,max=1,style={'slider-color':(1,0,0,0.5)})
w.add_widget(cm)

cm2 = MTCircularSlider(pos=(w.width/2-100,w.height/2-100),radius=150,thickness=70,padding=5,sweep_angle=135,rotation=55,style={'slider-color':(1,1,0,0.5)})
w.add_widget(cm2)

cm3 = MTCircularSlider(pos=(300,200),radius=150,thickness=70,padding=5,sweep_angle=135,rotation=-55,style={'slider-color':(0,1,0,0.5)})
w.add_widget(cm3)

cm4 = MTCircularSlider(pos=(300,600),radius=200,thickness=70,padding=5,sweep_angle=360,rotation=0,style={'slider-color':(0,0,1,0.5)})
w.add_widget(cm4)

runTouchApp()
