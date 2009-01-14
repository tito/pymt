from pymt import *
from pyglet import *
from pyglet.gl import *

import pickle


class GLWindow(MTRectangularWidget):
	def __init__(self,parent=None, size=(640,480), pos=(0,0)):
		MTRectangularWidget.__init__(self, parent=parent,size=(640,480), pos=(0,0))
		self.model = bunny = OBJ('monkey.obj')
		self.draw_color = (1.0,1.0,1.0)
		self.touch_position = {}
		self.rot_x, self.rot_y = 0.0, 0.0
		self.rotation_matrix = (GLfloat * 16)()
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		glGetFloatv(GL_MODELVIEW_MATRIX, self.rotation_matrix)


	def on_draw(self):
		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		glEnable(GL_NORMALIZE)
		glEnable(GL_DEPTH_TEST)
		
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glLoadIdentity()
		gluPerspective(60.,self.width/float(self.height) , 1., 100.)
		
		glMatrixMode(GL_MODELVIEW)
		glPushMatrix()
		glLoadIdentity()
		glTranslatef(0.0,0.0,-3.0)
		
		self.draw()
		
		glPopMatrix()
		glMatrixMode(GL_PROJECTION)
		glPopMatrix()

	def draw(self):
		glMultMatrixf(self.rotation_matrix)
		glRotatef(180.0, 0,0,1)
		glRotatef(90.0, 1,0,0)
		self.model.draw()



	def on_touch_down(self, touches, touchID, x, y):
		self.touch_position[touchID] = (x,y)
	
	def on_touch_move(self, touches, touchID, x, y):
		dx = 100.0*(x-self.touch_position[touchID][0])/float(self.width)
		dy = 100.0*(y-self.touch_position[touchID][1])/float(self.height)		
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		glRotatef(dx, 0,1,0)
		glRotatef(-dy, 1,0,0)
		glMultMatrixf(self.rotation_matrix)
		glGetFloatv(GL_MODELVIEW_MATRIX, self.rotation_matrix)
	
		self.touch_position[touchID] = (x,y)
	
	def on_touch_up(self, touches, touchID, x, y):
		del self.touch_position[touchID]

w = MTWindow()
w.set_fullscreen()
w.add_widget( GLWindow(size=(w.width, w.height)) )

runTouchApp()
