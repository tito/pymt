from pymt import *
from pyglet.gl import *
from pymt.ui import *

class MTInnerWindow(MTScatterWidget):

    def __init__(self, **kargs):
        super(MTInnerWindow, self).__init__(**kargs)

        self.color=(1,1,1,0.5)
        self.border = 20

        self.needs_redisplay = True
        self.window_fbo = Fbo(size=self.size)

        self.container = MTRectangularWidget(pos=(0,0),size=self.size)
        super(MTInnerWindow, self).add_widget(self.container)




    def add_widget(self, w):
        self.container.add_widget(w)

    def get_parent_window(self):
        return self.app_container

    def on_resize(self, w,h):
        self.resize_fbo(w,h)

    def resize_fbo(self, w, h, force=False):
        if abs(w-self.window_fbo.size[0]) > 50 or force:
            self.window_fbo = Fbo(size=(w,h))
            self.container.size = (w,h)
            self.needs_redisplay = True


    def on_touch_up(self, touches, touchID, x,y):
        #force correct resize on touch up...this way we guarantee its always exactly correct when resie is done
        if super(MTInnerWindow, self).on_touch_up( touches, touchID, x,y):
            scale = self.get_scale_factor()
            self.resize_fbo(int(self.width*scale), int(self.height*scale), force=True)
            return True


    def to_local(self,x,y):
        self.new_point = matrix_inv_mult(self.transform_mat, (x,y,0,1)) * self.get_scale_factor()
        return (self.new_point.x, self.new_point.y)

    def collide_point(self, x,y):
        scaled_border = int(self.border * (1.0/self.get_scale_factor()))
        local_coords = super(MTInnerWindow,self).to_local(x,y)
        left, right = -scaled_border, self.width+scaled_border*2
        bottom,top = -scaled_border,self.height+scaled_border*2
        if local_coords[0] > left and local_coords[0] < right \
           and local_coords[1] > bottom and local_coords[1] < top:
            self.needs_redisplay = True
            return True
        else:
            return False


    def draw(self):
        enable_blending()
        glColor4d(*self.color)
        scaled_border = int(self.border * (1.0/self.get_scale_factor()))
        drawRoundedRectangle((-scaled_border, -scaled_border), (self.width+scaled_border*2, self.height+scaled_border*2))
        disable_blending()

    def on_draw(self):
        if self.needs_redisplay or True:
            self.window_fbo.bind()
            self.container.dispatch_event('on_draw')
            self.window_fbo.release()
            self.needs_redisplay = False

        glPushMatrix()
        glMultMatrixf(self.transform_mat)
        self.draw()
        drawTexturedRectangle(self.window_fbo.texture, (0,0), self.size)
        glPopMatrix()
