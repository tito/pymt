import pyglet
from pyglet.gl import *
from pymt import * 
from random import random




shader = Shader(
	vertex_source   = None,
	
	fragment_source = """
		uniform sampler2D tex;
			void main()
			{
				vec4 color = texture2D(tex,gl_TexCoord[0].st);
				color = color*gl_Color;
				gl_FragColor = vec4(color.r, color.g, color.b, color.a );
			}
		"""
)


setBrush('particle.png', 10)

label = pyglet.text.Label('', font_size=10,anchor_x="left", anchor_y="top")
label2 = pyglet.text.Label('', font_size=8,anchor_x="left", anchor_y="top")
crosshair = pyglet.sprite.Sprite(pyglet.image.load('crosshair.png'))
crosshair.scale = 0.6




w = TouchWindow()
#w.set_fullscreen()

touchPositions = {}

@w.event
def on_touch_down(touches, touchID, x,y):
	color = (random(), random(), random())
	touchPositions[touchID] = [(touchID,color,x,y)]

@w.event
def on_touch_up(touches, touchID,x,y):
	del touchPositions[touchID]

@w.event
def on_touch_move(touches, touchID, x, y):
        touchPositions[touchID].append((x,y))


def drawLabel(x,y, ID):
	label.text = "touch["+ str(ID) +"]"
	label2.text = "x:"+str(int(x))+" y:"+str(int(y))
	label.x = label2.x = x +20
	label.y = label2.y = y +20
	label2.y -= 20
	label.draw()
	label2.draw()
	crosshair.x = x -12
	crosshair.y = y -12
	crosshair.draw()
	

@w.event
def on_draw():
	glClearColor(0.4,0.4,0.4,1.0)
	w.clear()
	for p in touchPositions:
		touchID,color,x,y = touchPositions[p][0]
		for pos in touchPositions[p][1:]:
			shader.use()
			glColor3d(*color)
			paintLine( (x, y, pos[0], pos[1]) )
			x, y = pos
			shader.stop()
		drawLabel(x,y, touchID)


runTouchApp()
