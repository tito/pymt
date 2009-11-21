#!/usr/bin/env python

from pymt import *
from OpenGL.GL import *
from time import gmtime, strftime



class DotBox(MTWidget):
    def __init__(self, **kwargs):
        super(DotBox, self).__init__(**kwargs)
        self.rotation = 0
        
    def draw(self):
        with gx_matrix:            
            glTranslated(self.x+self.width/2,self.y+self.height/2,0)
            glRotated(int(self.rotation),0,0,1)
            glTranslated(-self.x-self.width/2,-self.y-self.height/2,0)            
            set_color(*self.style.get('bg-color'))
            drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)
            set_color(0.0,0.0,0.0,1)
            drawCircle(pos=(self.x+10,self.y+30),radius=10)
        
    def do(self,*largs):
       for arg in largs:
            if arg.set_widget(self):
                arg.start(self)
    


w =  MTWindow()

circ = DotBox(pos=(100,100),style={'bg-color':(1.0,0.0,0.0),'border-radius': 0})
w.add_widget(circ)

circ2 = DotBox(pos=(400,600),style={'bg-color':(0.0,0.0,1.0),'border-radius': 0})
w.add_widget(circ2)

mov = Animation(duration=3,pos=(400,300),style={'bg-color':(0.0,1.0,.0),'border-radius': 20},rotation=90, size=(300,300))
"""
circ3 = DotBox(pos=(200,100),style={'bg-color':(0.0,1.0,1.0),'border-radius': 5})
w.add_widget(circ3)
"""
sq = DotBox(pos=(300,300),style={'bg-color':(1.0,0.0,1.0),'border-radius': 0})
w.add_widget(sq)

movX = Animation(duration=0.5,x=400)
movY = Animation(duration=2,y=500)
rot = Animation(duration=3,rotation=720)
col = Animation(duration = 5, style={'bg-color':(1.0,0.0,0.0)})

#movXY = movX & rot & movY & col

seqXY = movX + movY + rot

#delay = Delay(duration=5)

@circ.event
def on_animation_complete(*largs):
    print "Animation 1 Completed"
    #print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
@circ2.event
def on_animation_complete(*largs):
    print "Animation 2 Completed"
    
@sq.event
def on_animation_complete(*largs):
    print "sq complete"
    #print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

#print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
but = MTButton(label="Start",pos=(10,10))
w.add_widget(but)
@but.event
def on_press(*largs):
    sq.do(seqXY)
    #print strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
    #circ.do(mov)
    #mov.animate(circ2)
    #circ3.do(Animation(duration=3,x=600,rotation=360,style={'bg-color':(1.0,1.0,.0),'border-radius': 10})) #Creates new animation object everytime you press creates undesireable results
runTouchApp()