# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Picture Viewer'
PLUGIN_AUTHOR = 'Thomas Hansen'
PLUGIN_DESCRIPTION = 'Demonstration of MTScatterImage object'

from pymt import *
import os
import random
from OpenGL.GL import *

def handle_image_move(image, *largs):
    w = image.get_parent_window()
    if not w:
        return
    if image.x < 0:
        image.pos = (0, image.y)
    if image.y < 0:
        image.pos = (image.x, 0)
    if image.x > w.width:
        image.pos = (w.width, image.y)
    if image.y > w.height:
        image.pos = (image.x, w.height)

def draw_border(image, *largs):
    set_color(1,1,1,1)
    with gx_matrix:
        glTranslatef(image.center[0], image.center[1], 0)
        glRotated(image.rotation,0,0,1)
        glScalef(image._scale,image._scale,1)
        drawRectangle(pos=(-image.width/2-5,-image.height/2-5), size=(image.width+10, image.height+10))

def pymt_plugin_activate(w, ctx):
    ctx.c = MTKinetic()
    for i in range(6):
        img_src = '../pictures/images/pic'+str(i+1)+'.jpg'
        x = int(random.uniform(100, w.width-100))
        y = int(random.uniform(100, w.height-100))
        rot = random.uniform(0, 360)
        scale = random.uniform(3, 10)
        b = MTScatterImage(filename=img_src, pos=(x,y), rotation=rot)
        b.size = b.image.width / scale, b.image.height / scale
        b.push_handlers(on_move=curry(handle_image_move, b))
        b.push_handlers(on_draw=curry(draw_border, b))
        ctx.c.add_widget(b)
    w.add_widget(ctx.c)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
