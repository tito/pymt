from pymt import *
from pyglet import *
from pyglet.gl import *

import pickle


class GLWindow(TouchWindow):
    def __init__(self):
        config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, vsync=0)
        TouchWindow.__init__(self, config)
	self.model = bunny = OBJ('monkey.obj')
        self.draw_color = (1.0,1.0,1.0)
        self.touch_position = {}
        self.rot_x, self.rot_y = 0.0, 0.0
        
    def on_draw(self):
        global batch
        self.clear()

	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)
	glEnable(GL_NORMALIZE)
	glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.,self.width/float(self.height) , 1., 100.)
        
        glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
        glTranslatef(0.0,0.0,-3.0)
        
        glRotatef(-self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)
	glRotatef(180.0, 0,0,1)
        glRotatef(90.0, 1,0,0) 
        self.model.draw() 
        
            
    def on_touch_down(self, touches, touchID, x, y):
        self.touch_position[touchID] = (x,y)

        
    def on_touch_move(self, touches, touchID, x, y):
        self.rot_x += 100.0*(y-self.touch_position[touchID][1])/self.width
        self.rot_y += 100.0*(x-self.touch_position[touchID][0])/self.height
	self.touch_position[touchID] = (x,y)

        
    def on_touch_up(self, touches, touchID, x, y):
        del self.touch_position[touchID]
        

    
    
w = GLWindow()
w.set_fullscreen()
runTouchApp()
