from pymt import *
from OpenGL.GL import *

class MTSprite(MTWidget):
    def __init__(self, **kwargs):
        super(MTSprite, self).__init__(**kwargs)
        self.rotation = 0
        self.filename		= kwargs.get('filename')
        self.image     = pymt.Image(self.filename)
        self.size           = self.image.size
        self.scale = 1.0
        self.intial_pos = self.pos
        
    def draw(self):
        with gx_matrix:            
            glTranslated(self.x+self.width/2,self.y+self.height/2,0)
            glRotated(int(self.rotation),0,0,1)
            glTranslated(-self.x-self.width/2,-self.y-self.height/2,0)            
            set_color(*self.style.get('bg-color'))
            self.image.pos  = self.pos
            self.image.scale= self.scale
            self.size = self.image.size
            self.image.draw()
    
    def reset(self):
        self.size = self.image.size
        self.scale = 1.0
        self.pos = self.intial_pos
        self.rotation = 0
        self.image.pos  = self.pos
        self.image.scale= self.scale


m = MTWindow()

#Set up buttons
but_layout = MTBoxLayout(cols=4)
m.add_widget(but_layout)
reset = MTButton(label="Reset",style={'bg-color':(0,0,0)})
but_layout.add_widget(reset)

simple = MTButton(label="Simple",style={'bg-color':(0,0,0)})
but_layout.add_widget(simple)

sequence = MTButton(label="Sequence",style={'bg-color':(0,0,0)})
but_layout.add_widget(sequence)

parallel = MTButton(label="parallel",style={'bg-color':(0,0,0)})
but_layout.add_widget(parallel)

but_layout.x = m.width/2-but_layout.width/2 #Align button at the bottom-center


#Add Objects
greeny = MTSprite(filename="icons/greeny.png" ,pos=(100,150))
m.add_widget(greeny)

#Construct Animations
movX = Animation(duration=1, x=m.width/2-greeny.width/2)
movY = Animation(duration=1, y=m.height/2-greeny.height/2)
movXY = Animation(duration=1, pos=(m.width/2-greeny.width/2, m.height/2-greeny.height/2)) #Move to center
rot360 = Animation(duration=2, rotation=720)
scale = Animation(duration=1.5, scale=2)

seq = movX + movY + rot360 + scale

pll = movX & movY & rot360 & scale

#handle button press
@reset.event
def on_press(*largs):
    greeny.reset()
    
@simple.event
def on_press(*largs):
    greeny.do(movXY)
    
@sequence.event
def on_press(*largs):
    greeny.do(seq)

@parallel.event
def on_press(*largs):
    greeny.do(pll)

runTouchApp()
