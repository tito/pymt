from __future__ import with_statement

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = '3D Viewer'
PLUGIN_AUTHOR = 'Thomas Hansen'
PLUGIN_EMAIL = 'thomas.hansen@gmail.com'


from pymt import *
from OpenGL.GL import *
from OpenGL.GLU import *


class GLPerspectiveWidget(MTWidget):
    """Sets up 3d projection in on_draw function and then calls seld.draw, origin in the center"""
    def __init__(self, **kargs):
        super(GLPerspectiveWidget, self).__init__(**kargs)
        self.needs_redisplay = True
        self.fbo = Fbo(size=self.size)

    def on_resize(self, w, h):
        self.size = w, h
        del self.fbo
        self.fbo = Fbo(size=self.size)
        self.needs_redisplay = True

    def on_draw(self):
        if self.needs_redisplay:
            with self.fbo:
                self.draw3D()
        glColor3f(1,1,1)
        drawTexturedRectangle(self.fbo.texture, size=self.size)

    def draw3D(self):
        glPushAttrib(GL_VIEWPORT_BIT)
        glViewport(0,0,self.fbo.size[0], self.fbo.size[1])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
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

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glPopAttrib()
        self.needs_redisplay = False


class ModelViewer(GLPerspectiveWidget):
    def __init__(self, **kargs):
        GLPerspectiveWidget.__init__(self, **kargs)
        self.touch_position = {}
        self.model = bunny = OBJ('../3Dviewer/monkey.obj')
        self.rotation_matrix = None
        self.reset_rotation()
        self.touch1, self.touch2 = None, None
        self.zoom = 1.0


    def reset_rotation(self):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        self.rotation_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        glPopMatrix()

    def draw(self):
        glMultMatrixf(self.rotation_matrix)
        #glRotatef(180.0, 0,0,1)
        glRotatef(90.0, 1,0,0)
        glScalef(self.zoom, self.zoom, self.zoom)
        self.model.draw()

    def check_touches(self, touches):
        if self.touch1 and not self.touch1 in touches:
            if self.touch1 in self.touch_position:
                del self.touch_position[self.touch1]
            self.touch1 = None
        if self.touch2 and not self.touch2 in touches:
            if self.touch2 in self.touch_position:
                del self.touch_position[self.touch2]
            self.touch2 = None

    def on_touch_down(self, touch):
        self.check_touches(getCurrentTouches())
        self.touch_position[touch.id] = (touch.x, touch.y)
        if len(self.touch_position) == 1:
            self.touch1 = touch
            touch.grab(self)
        elif len(self.touch_position) == 2:
            self.touch2 = touch
            touch.grab(self)
            v1 = Vector(*self.touch_position[self.touch1.id])
            v2 = Vector(*self.touch_position[self.touch2.id])
            self.scale_dist = v1.distance(v2)

    def on_touch_move(self, touch):
        if not touch.grab_current == self:
            return
        self.check_touches(getCurrentTouches())
        dx, dy = 0,0
        scale = 1.0
        angle = 0.0
        if self.touch1 and self.touch2 and self.touch_position.has_key(self.touch1.id) and self.touch_position.has_key(self.touch2.id):
            v1 = Vector(*self.touch_position[self.touch1.id])
            v2 = Vector(*self.touch_position[self.touch2.id])
            new_dist = v1.distance(v2)
            zoomfactor = new_dist/self.scale_dist
            if zoomfactor > 1.0:
                zoomfactor = 1.0 + (zoomfactor - 1.0) * 0.5
            else:
                zoomfactor = 1.0 - abs(1.0 - zoomfactor ) * 0.5
            self.zoom *= zoomfactor
            self.scale_dist = new_dist


            # compute rotation angle
            old_line = v1 - v2
            new_line = None
            if self.touch1.id == touch.id:
                new_line = Vector(touch.x, touch.y) - v2
            else:
                new_line = v1 - Vector(touch.x, touch.y)

            angle = -1.0 * old_line.angle(new_line)
        elif touch.id in self.touch_position:
            dx = 200.0*(touch.x-self.touch_position[touch.id][0])/float(self.width)
            dy = 200.0*(touch.y-self.touch_position[touch.id][1])/float(self.height)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glRotatef(angle, 0,0,1)
        glRotatef(dx, 0,1,0)
        glRotatef(-dy, 1,0,0)
        glMultMatrixf(self.rotation_matrix)
        self.rotation_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        glPopMatrix()
        self.touch_position[touch.id] = (touch.x, touch.y)
        self.needs_redisplay = True

    def on_touch_up(self, touch):
        if not touch.grab_current == self:
            return
        self.check_touches(getCurrentTouches())
        if touch.id in self.touch_position:
            del self.touch_position[touch.id]
            self.needs_redisplay = True

def pymt_plugin_activate(root, ctx):
    ctx.mv = ModelViewer(size=(root.width,root.height))
    root.add_widget(ctx.mv)

def pymt_plugin_deactivate(root, ctx):
    root.remove_widget(ctx.mv)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
