from pymt import *
from pyglet.gl import *
from pymt.ui import *

iconPath = os.path.join(os.path.dirname(pymt.__file__), 'data', 'icons','')

class MTInnerWindow(MTScatterWidget):

    def __init__(self, **kargs):
        super(MTInnerWindow, self).__init__(**kargs)

        self.color=(1,1,1,0.5)
        self.border = 20

        self.needs_redisplay = True
        self.window_fbo = Fbo(size=self.size)

        self.container = MTRectangularWidget(pos=(0,0),size=self.size)
        super(MTInnerWindow, self).add_widget(self.container)

        self.setup_controlls()
        self.locked = False



    def setup_controlls(self):
        self.controlls = HVLayout()
        button_pause = MTImageButton(filename=iconPath+'pause.png', scale=0.5)
        button_pause.push_handlers(on_release=self.toggle_locked)
        self.controlls.add_widget(button_pause)

        button_fullscreen = MTImageButton(filename=iconPath+'fullscreen.png',scale=0.5)
        button_fullscreen.push_handlers(on_release=self.fullscreen)
        self.controlls.add_widget(button_fullscreen)

        button_close = MTImageButton(filename=iconPath+'stop.png',scale=0.5)
        button_close.push_handlers(on_release=self.close)
        self.controlls.add_widget(button_close)


        self.controlls.x, self.controlls.y = self.width/2 - button_pause.width*3/2, -button_pause.height*1.7

    def toggle_locked(self, touchID=None, x=0, y=0 ):
        if self.locked:
            super(MTInnerWindow, self).add_widget(self.container)
            self.locked = False
            self.resize_fbo(self.width, self.height, force=True)
        else:
            super(MTInnerWindow, self).remove_widget(self.container)
            self.locked = True


    def fullscreen(self,touchID=None, x=0, y=0):
        root_win = self.parent.get_parent_window()
        root_win.children = []
        self.container.size = root_win.parent.size
        root_win.add_widget(root_win.parent.sim)
        root_win.add_widget(self.container)

    def close(self, touchID=None, x=0, y=0):
        print "closing window"
        self.parent.remove_widget(self)

    def add_widget(self, w):
        self.container.add_widget(w)

    def get_parent_window(self):
        return self.app_container

    def on_resize(self, w,h):
        if not self.locked:
            self.resize_fbo(w,h)
        for button in self.controlls.children:
            button.scale = 0.5/self.get_scale_factor()
        self.controlls.x, self.controlls.y = self.width/2 - self.controlls.children[0].width*3/2, -self.controlls.children[0].height*1.7

    def resize_fbo(self, w, h, force=False):
        if abs(w-self.window_fbo.size[0]) > 50 or force:
            self.window_fbo = Fbo(size=(w,h))
            self.container.size = (w,h)
            self.needs_redisplay = True

    def on_touch_down(self, touches, touchID, x,y):
        lx,ly = super(MTInnerWindow, self).to_local(x,y)
        if self.controlls.dispatch_event('on_touch_down', touches, touchID, lx, ly):
            return True
        return super(MTInnerWindow, self).on_touch_down( touches, touchID, x,y)

    def on_touch_move(self, touches, touchID, x,y):
        lx,ly = super(MTInnerWindow, self).to_local(x,y)
        if self.controlls.dispatch_event('on_touch_move', touches, touchID, lx, ly):
            return True
        return super(MTInnerWindow, self).on_touch_move( touches, touchID, x,y)

    def on_touch_up(self, touches, touchID, x,y):
        lx,ly = super(MTInnerWindow, self).to_local(x,y)
        if self.controlls.dispatch_event('on_touch_up', touches, touchID, lx, ly):
            return True
        #force correct resize on touch up...this way we guarantee its always exactly correct when resie is done
        if super(MTInnerWindow, self).on_touch_up( touches, touchID, x,y):
            if not self.locked:
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
        glPushMatrix()
        drawRectangle(((self.width/2)-(scaled_border*2.5), -scaled_border), (scaled_border*5, -scaled_border*1.2))
        glPopMatrix()
        disable_blending()


    def on_draw(self):
        if not self.locked:
            self.window_fbo.bind()
            self.container.dispatch_event('on_draw')
            self.window_fbo.release()
            self.needs_redisplay = False

        glPushMatrix()
        glMultMatrixf(self.transform_mat)
        self.draw()
        drawTexturedRectangle(self.window_fbo.texture, (0,0), self.size)
        if self.locked:
            enable_blending()
            glColor4f(0.5,0.5,1, 0.3)
            drawRectangle((0,0), self.size)
            disable_blending()
        self.controlls.dispatch_event('on_draw')

        glPopMatrix()
