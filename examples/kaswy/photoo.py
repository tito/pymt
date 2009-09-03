#photoo from kaswy 
#Website http://kaswy.free.fr
#Depend of PyMT from  Thomas Hansen

from __future__ import with_statement
import sys
from math import sqrt
from pymt import *
from pyglet.gl import *
from PIL import Image #just for resizing your source image to a 2n sized image (texture)

res = 15
Data = []
vertexImpact = {}

class GLWindow(MTWindow):
	def __init__(self):
		super(GLWindow, self).__init__()
		self.draw_color = (1.0,1.0,1.0)
		self.touch_position = {}
		self.rot_x, self.rot_y = 0.0, 0.0

	def on_draw(self):
		self.clear()
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluOrtho2D(0,res-1,0,res-1)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		#glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        with gx_texture(image):
            Vertex = 0
            for y in range(res-1):
                glBegin(GL_QUAD_STRIP)
                for x in range(res):
                    xyz = Data[Vertex]
                    glTexCoord2f(float(x)/res,float(y)/res);
                    glVertex2f(xyz[0],xyz[1])
                    Vertex += 1
                    xyz = Data[Vertex]
                    glTexCoord2f(float(x)/res,float(y+1)/res);
                    glVertex2f(xyz[0],xyz[1])
                    Vertex += 1
                glEnd()

	def on_touch_down(self, touches, touchID, x, y):
		vertexImpact[touchID]=[(x,y)]
		for xy in Data:
			impact = ((sqrt(abs((xy[0]*dx-x)**2 + (xy[1]*dy-y)**2))/diag)**1.5)*60000 
			vertexImpact[touchID].append(impact)

	def on_touch_move(self, touches, touchID, x, y):
		startpos = vertexImpact[touchID][0]
		deplx=x-startpos[0]
		deply=y-startpos[1]
		vertex = 0
		for impact in vertexImpact[touchID][1:]:
			if impact < 200: impact = 200.0
			Data[vertex][0]+= deplx/impact
			Data[vertex][1]+= deply/impact
			vertex+=1
		vertexImpact[touchID][0]=(x,y)
		imp=1
		for xy in Data:
			impact = ((sqrt(abs((xy[0]*dx-x)**2 + (xy[1]*dy-y)**2))/diag)**1.5)*40000
			if vertexImpact[touchID][imp] > impact :vertexImpact[touchID][imp] = impact
			imp+=1

        def on_touch_up(self, touches, touchID, x, y):
            del vertexImpact[touchID]
		

def createMesh():
	for y in range(res):
		for x in range(res):
			Data.append([x,y])
			Data.append([x,y+1])

def loadTextures():
		global image
		src = 'portrait.jpg'
		image = Image.open(src)
		print "image size is :",image.size
		size = 512, 512
		if image.size != size:
			print "Resizing image ...."
			image = image.resize(size,Image.ANTIALIAS)
			image.save(src, "JPEG")
		image = pyglet.image.load(src).get_texture()

print "Photoo manipulation Multitouch demo"
print "\n"
print "Put your photo file named 'portrait.jpg' in the directory"
print "Launch photoo"
print  "\n"
print "Have fun !!!!!!!!!"
createMesh()
loadTextures()
w = GLWindow()
w.set_fullscreen()
dx=w.width/(res-1)
dy=w.height/(res-1)
diag=sqrt(w.width**2+w.height**2)

runTouchApp()
sys.exit()
