import pyglet
from pyglet.gl import *
from pymt import * 










frag_src = """
uniform sampler2D tex;
void main()
{
	vec4 color = texture2D(tex,gl_TexCoord[0].st);
	gl_FragColor = vec4(color.r, color.g, color.b, color.a );
}
"""




label = pyglet.text.Label('Go Hawks!', font_size=10,anchor_x="left", anchor_y="top")
label2 = pyglet.text.Label('Go Hawks!', font_size=8,anchor_x="left", anchor_y="top")
crosshair = pyglet.sprite.Sprite(pyglet.image.load('crosshair.png'))
crosshair.scale = 0.6

shader = Shader(None, frag_src)
point_sprite_img = pyglet.image.load('particle.png')
point_sprite = point_sprite_img.get_texture()

w = TouchWindow()
#w.set_fullscreen()

touchPositions = {}

@w.event
def on_touch_down(touches, touchID, x,y):
	touchPositions[touchID] = [(touchID,x,y)]

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
	w.clear()
        for p in touchPositions:
        	touchID,x,y = touchPositions[p][0]

		for pos in touchPositions[p][1:]:
			shader.use()
			glBindTexture(point_sprite.target, point_sprite.id)
			glEnable(GL_POINT_SPRITE_ARB); 
			glTexEnvi(GL_POINT_SPRITE_ARB, GL_COORD_REPLACE_ARB, GL_TRUE);
			glPointSize(16)
			draw(2,GL_LINES, ( 'v2f', (x, y, pos[0], pos[1]) ))
			x, y = pos
			glBindTexture(point_sprite.target, 0)
			shader.stop()
                drawLabel(x,y, touchID)

runTouchApp()
