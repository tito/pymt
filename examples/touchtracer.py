import pyglet
from pyglet.gl import *
from pymt import * 

touchPositions = {}
label = pyglet.text.Label('Go Hawks!', font_size=10,anchor_x="left", anchor_y="top")
label2 = pyglet.text.Label('Go Hawks!', font_size=8,anchor_x="left", anchor_y="top")
crosshair = pyglet.sprite.Sprite(pyglet.image.load('data/crosshair.png'))
crosshair.scale = 0.6

w = TouchWindow()
w.set_fullscreen()

@w.event
def on_touch_down(touches, touchID, x,y):
	touchPositions[touchID] = [(touchID,x,y)]

@w.event
def on_touch_up(touches, touchID,x,y):
	del touchPositions[touchID]

@w.event
def on_touch_move(touches, touchID, x, y):
                touchPositions[touchID].append((x,y))

@w.event
def on_draw():
	w.clear()
        for p in touchPositions:
        	touchID,x,y = touchPositions[p][0]

		for pos in touchPositions[p][1:]:
			drawLine( [(x, y), pos] )
			x, y = pos

                label.text = "touch["+ str(touchID) +"]"
		label2.text = "x:"+str(int(x))+" y:"+str(int(y))
                label.x = label2.x = x +20
                label.y = label2.y = y +20
		label2.y -= 20
                label.draw()
		label2.draw()
		crosshair.x = x -12
		crosshair.y = y -12
		crosshair.draw()

runTouchApp()
