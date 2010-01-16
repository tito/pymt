# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Picture Viewer'
PLUGIN_AUTHOR = 'Thomas Hansen'
PLUGIN_DESCRIPTION = 'Demonstration of MTScatterImage object'

from pymt import *
import os
import random
from OpenGL.GL import *

current_dir = os.path.dirname(__file__)

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
        glScalef(image._scale, image._scale, 1)
        b = 5 * (1 / image._scale)
        drawRectangle(pos=(-image.width/2-b,-image.height/2-b),
                      size=(image.width+b*2, image.height+b*2))

def image_on_load(scatter):
    scatter.scale = 1 / random.uniform(3, 10)

def pymt_plugin_activate(w, ctx):
    ctx.c = MTKinetic()
    for i in range(6):
        img = Loader.image(os.path.join(current_dir, 'images', 'pic%d.jpg' % (i+1)))
        x = int(random.uniform(100, w.width-100))
        y = int(random.uniform(100, w.height-100))
        rot = random.uniform(0, 360)
        scale = random.uniform(3, 10)
        b = MTScatterImage(image=img, pos=(x,y), rotation=rot)
        img.connect('on_load', curry(image_on_load, b))
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
