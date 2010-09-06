from __future__ import with_statement

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = '3D Painting'
PLUGIN_AUTHOR = 'Thomas Hansen'
PLUGIN_EMAIL = 'thomas.hansen@gmail.com'

import os
from pymt import *
from OpenGL.GL import *
from OpenGL.GLU import *

current_dir = os.path.dirname(__file__)
particle_fn = os.path.join(current_dir, 'particle.png')
set_brush(particle_fn, 10)

class GL3DPerspective:
    """
    Handy Class for use with python 'with' statement.
    on enter: sets the openGL pojection matrix to a standart perspective projection, enables, lighting, normalizing fo normals and depth test
    on exit: restores matrices and states to what they were before
    """
    def __init__(self, angle=60.0, aspect=4.0/3.0, near=1.0, far=100.0):
        self.angle = angle
        self.aspect = aspect
        self.near = near
        self.far = far

    def __enter__(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)
        glEnable(GL_DEPTH_TEST)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluPerspective(self.angle,self.aspect , self.near, self.far)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(0.0,0.0,-3.0)


    def __exit__(self, type, value, traceback):
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)



class ModelPainter(MTWidget):

    def __init__(self, **kwargs):
        super(ModelPainter, self).__init__(**kwargs)

        #the persepctuve we use for drawing teh 3D world
        self.perspective = GL3DPerspective()

        #load the obj model file
        #set compat=False, mneans we have to setup lighting etc ourselves
        #but since we need to disable ligthing during picking, we need this here
        self.model = OBJ(os.path.join(current_dir, 'cow.obj'), compat=False)

        #texture and FBO used for picking
        self.picking_image = Image.load(os.path.join(current_dir, 'picking.png'))
        self.picking_texture = self.picking_image.get_texture()
        self.fbo = Fbo(size=self.size)
        self.painting_fbo = Fbo(size=(512,512))

        #initialize the painting buffer as white
        with self.painting_fbo:
            glClearColor(1,1,1,1)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #stuff for rotating and keeping track of touches
        self.touch_position = {}
        self.rotation_matrix = None
        self.reset_rotation()
        self.touch1, self.touch2 = None, None
        self.zoom = 3.0

        self.mode = 'painting'
        self.has_moved = True


    def on_resize(self, w, h):
        del self.fbo
        self.fbo = Fbo(self.size)


    def reset_rotation(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        self.rotation_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        glPopMatrix()


    def rotate_scene(self, x,y,z):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glRotatef(z, 0,0,1)
        glRotatef(x, 0,1,0)
        glRotatef(y, 1,0,0)
        glMultMatrixf(self.rotation_matrix)
        self.rotation_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        glPopMatrix()
        self.has_moved = True


    def on_draw(self):
        #draw into FBO
        glClearColor(0.3,0.6,0.3,0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        with DO(self.perspective, gx_texture(self.painting_fbo.texture)):
            self.draw()

        #display teh FBO contents
        glColor3f(1,1,1)
        #drawTexturedRectangle(self.fbo.texture, size=self.size)
        #drawTexturedRectangle(self.painting_fbo.texture, size=(256,256))
        #drawTexturedRectangle(self.picking_texture.id,pos=(256,0), size=(256,256))



    def draw(self):
        glMultMatrixf(self.rotation_matrix)
        glRotatef(90.0, 1,0,0)
        glScalef(self.zoom, self.zoom, self.zoom)
        glColor3f(1,1,1)
        self.model.draw()


    def draw_picking(self):
        glDisable(GL_LIGHTING)
        glColor3f(1,1,1)
        with gx_texture(self.picking_texture):
            self.draw()


    def pick(self, x,y):
        pick = None
        with self.fbo:
            if self.has_moved:
                glClearColor(0,0,0,0)
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                with self.perspective:
                    self.draw_picking()
                self.has_moved = False
            pick = glReadPixels(int(x), int(y), 1, 1, GL_RGB, GL_UNSIGNED_BYTE)
            pick = map(ord, pick)
        return pick[0]*4, 1024 - pick[1]*4

    def paint(self, x, y):
        x,y =  self.pick(x,y)
        s = self.painting_fbo.size
        x /= 1024 / s[0]
        y /= 1024 / s[1]

        with self.painting_fbo:
            glColor3f(.1, .1, 0)
            drawCircle(pos=(x,y), radius=8)
            #paintLine([x,y,x,y])


    def on_touch_down(self, touch):
        self.touch_position[touch.id] = (touch.x, touch.y)

        #check if this touch should eb used to draw
        pick = self.pick(touch.x, touch.y)
        if pick[0] != 0 or pick[1] != 1024:
            touch.userdata['drawing'] = True
            return

        #if not, its going to be a touch that turns/scales the object
        touch.userdata['drawing'] = False
        if len(self.touch_position) == 1:
            self.touch1 = touch.id
        elif len(self.touch_position) == 2:
            self.touch1, self.touch2 = self.touch_position.keys()
            v1 = Vector(*self.touch_position[self.touch1])
            v2 = Vector(*self.touch_position[self.touch2])
            self.scale_dist = v1.distance(v2)




    def on_touch_move(self, touch):


        #if its one used to draw, but its now away from teh model
        #just dont do anything, until its back on teh model, or gone
        if touch.userdata.get('drawing'):
            pick = self.pick(touch.x, touch.y)
            #if its still on the model, draw on it
            if pick[0] != 0 or pick[1] != 1024:
                self.paint(touch.x, touch.y)
            return

        #if we got here, its a touch to turn/scale the model
        dx, dy, angle = 0,0,0
        #two touches:  scale and rotate around Z
        if  self.touch_position.has_key(self.touch1) and self.touch_position.has_key(self.touch2):
            v1 = Vector(*self.touch_position[self.touch1])
            v2 = Vector(*self.touch_position[self.touch2])

            #compute scale factor
            new_dist = v1.distance(v2)
            zoomfactor = new_dist/self.scale_dist
            self.zoom *= zoomfactor
            self.scale_dist = new_dist

            # compute rotation angle
            old_line = v1 - v2
            new_line = Vector(touch.x, touch.y) - v2
            if self.touch1 != touch.id: new_line = v1 - Vector(touch.x, touch.y)
            angle = -1.0 * old_line.angle(new_line)

        else: #only one touch:  rotate using trackball method
            dx = 200.0*(touch.x-self.touch_position[touch.id][0])/float(self.width)
            dy = 200.0*(touch.y-self.touch_position[touch.id][1])/float(self.height)

        #apply the transformations we just computed
        self.rotate_scene(dx,-dy, angle)
        self.touch_position[touch.id] = (touch.x, touch.y)


    def on_touch_up(self, touch):
        del self.touch_position[touch.id]








def pymt_plugin_activate(root, ctx):
    ctx.mp = ModelPainter(size=(root.width,root.height))
    root.add_widget(ctx.mp)

def pymt_plugin_deactivate(root, ctx):
    root.remove_widget(ctx.mp)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
