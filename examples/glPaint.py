from pymt import *
from pyglet import *
from pyglet.gl import *

def drawCircle(pos=(0,0), color=(1.0,1.0,1.0)):
    x, y = pos
    glPushMatrix()
    glTranslated(x,y, 0)
    glColor3d(*color)
    gluDisk(gluNewQuadric(), 0, 10, 32,1)
    glPopMatrix()


def drawLine(points, color):
       p1, p2 = points[0], points[1]
       glLineWidth (20.0)
       if (color):
	       glColor3f(*color)
       glBegin(GL_LINES)
       glVertex2f( p1[0], p1[1] )
       glVertex2f( p2[0], p2[1] )
       glEnd()
       glLineWidth (1.0)


class ColorPicker:
	def __init__(self, width=200, height = 400):
		self.width, self.height = width, height
		#draw a rectangle on the left hand side
		self.vertex_list = pyglet.graphics.vertex_list(4,
                                          ('v2f', (40.0, 100.0,  float(width),100.0 ,  float(width),float(height)-50 ,  40.0, float(height)-50)) ,
                                          ('c4B', (0,0,0,255, 255,0,0,255, 255,255,0,255, 0,255,0,255) ) )
	def getColorForPoint(self,x,y):
		if x < self.width and y < self.height:
			return [float(x)/self.width, float(y)/self.height, 0.0]
		else: return None

	def draw(self):
		self.vertex_list.draw(GL_QUADS)


class PaintWindow(TouchWindow):
    def __init__(self):
        config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True, vsync=0)
        TouchWindow.__init__(self, config)
	self.set_fullscreen()
        self.touch_positions = {}
	self.color_picker = ColorPicker(height=self.height)
        
    def on_draw(self):  	
	for p in self.touch_positions:
		x,y = self.touch_positions[p][0][0],self.touch_positions[p][0][1]
		for pos in self.touch_positions[p][1:]:
			drawLine( [(x, y), (pos[0],pos[1])] ,pos[2])
			x, y = pos[0],pos[1]

	self.color_picker.draw()
            
    def on_touch_down(self, touches, touchID, x, y):
	col = self.color_picker.getColorForPoint(x,y)
        self.touch_positions[touchID] = [(x,y, col)]

        
    def on_touch_move(self, touches, touchID, x, y):
	col = self.color_picker.getColorForPoint(x,y)
        self.touch_positions[touchID].append((x,y,col))

        
    def on_touch_up(self, touches, touchID, x, y):
        del self.touch_positions[touchID]
        

    
    
w = PaintWindow()
runTouchApp()
