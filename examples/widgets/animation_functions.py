from pymt import *
from OpenGL.GL import *
import random, math

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

w = MTWindow(style={'bg-color':(0,0,0)})
getWindow().gradient = False

objlist = [] #List of sprites

for i in range(64):
    x = int(random.uniform(100, w.width-100))
    y = int(random.uniform(100, w.height-100))
    obj = MTSprite(pos=(x,y), filename="icons/clock.png")
    objlist.append(obj)
    w.add_widget(obj)

#Set up buttons
but_layout = MTGridLayout(cols=4,rows=2)
w.add_widget(but_layout)
randomize = MTButton(label="Randomize",style={'bg-color':(0,0,0)},height=50)
but_layout.add_widget(randomize)

grid = MTButton(label="Grid",style={'bg-color':(0,0,0)},height=50)
but_layout.add_widget(grid)

circular = MTButton(label="Circular",style={'bg-color':(0,0,0)},height=50)
but_layout.add_widget(circular)

bowtie = MTButton(label="Bow Tie",style={'bg-color':(0,0,0)},height=50)
but_layout.add_widget(bowtie)

but_layout.x = w.width/2-but_layout.width/2 #Align button at the bottom-center

#handle button press
@randomize.event
def on_press(*largs):
    anim_list = []
    for i in range(64):
        x = int(random.uniform(100, w.width-100))
        y = int(random.uniform(100, w.height-100))
        anim_list.append(Animation(duration=1.5, pos=(x,y), alpha_function="ease_in_out_back"))
    
    i = 0
    for obj in objlist:
        obj.do(anim_list[i])
        i += 1

@grid.event
def on_press(*largs):
    anim_list = []
    for i in range(8):
        for j in range(8):
            x = j*64+100
            y = i*64+40
            anim_list.append(Animation(duration=1.5, pos=(x,y), alpha_function="ease_in_out_back"))
    
    i = 0
    for obj in objlist:
        obj.do(anim_list[i])
        i += 1

@circular.event
def on_press(*largs):
    anim_list = []
    for i in range(64):
        teta = math.radians(8*i)
        x = 200 * math.cos(teta)+w.width/2
        y = 200 * math.sin(teta)+w.height/2
        anim_list.append(Animation(duration=1.5, pos=(x,y), alpha_function="ease_in_out_back"))
    
    i = 0
    for obj in objlist:
        obj.do(anim_list[i])
        i += 1        

@bowtie.event
def on_press(*largs):
    anim_list = []
    for i in range(64):
        teta = math.radians(8*i)
        x = 200 * math.cos(teta)+w.width/2
        y = 200 * math.sin(teta*2)+w.height/2
        anim_list.append(Animation(duration=1.5, pos=(x,y), alpha_function="ease_in_out_back"))

    i = 0
    for obj in objlist:
        obj.do(anim_list[i])
        i += 1        

runTouchApp()