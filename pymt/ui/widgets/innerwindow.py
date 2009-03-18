'''
Inner window: a lightweight window with fullscreen and resize ability
'''

from __future__ import with_statement
__all__ = ['MTInnerWindow']

import os
import pymt
from pyglet.gl import *
from ...graphx import gx_matrix, drawRectangle, set_color
from ...graphx import drawRoundedRectangle, drawTexturedRectangle
from ...vector import matrix_inv_mult
from rectangle import MTRectangularWidget
from scatter import MTScatterWidget
from button import MTImageButton
from layout.boxlayout import MTBoxLayout

iconPath = os.path.join(os.path.dirname(pymt.__file__), 'data', 'icons', '')

class MTInnerWindow(MTScatterWidget):

    def __init__(self, **kargs):
        super(MTInnerWindow, self).__init__(**kargs)

        self.color=(1,1,1,0.5)
        self.border = 20
        self.__w = self.__h = 0

        self.container = MTRectangularWidget(pos=(0,0),size=self.size)
        super(MTInnerWindow, self).add_widget(self.container)

        self.setup_controls()


    def setup_controls(self):
        self.controls = MTBoxLayout()

        button_fullscreen = MTImageButton(filename=iconPath+'fullscreen.png',scale=0.5)
        button_fullscreen.push_handlers(on_release=self.fullscreen)
        self.controls.add_widget(button_fullscreen)

        button_close = MTImageButton(filename=iconPath+'stop.png', scale=0.5)
        button_close.push_handlers(on_release=self.close)
        self.controls.add_widget(button_close)

        self.controls.pos = self.width/2, -button_fullscreen.height*1.7

    def fullscreen(self,touchID=None, x=0, y=0):
        root_win = self.parent.get_parent_window()
        root_win.children = []
        self.container.size = root_win.parent.size
        root_win.add_widget(root_win.parent.sim)
        root_win.add_widget(self.container)

    def close(self, touchID=None, x=0, y=0):
        self.parent.remove_widget(self)

    def add_widget(self, w):
        self.container.add_widget(w)

    def get_parent_window(self):
        return self.container

    def on_resize(self, w, h):
        # XXX remove this optim, and do it in scatter widget !
        if self.__w == w and self.__h == h:
            return
        self.__w, self.__h = w, h
        for button in self.controls.children:
            button.scale = 0.5/self.get_scale_factor()
        self.controls.pos = self.width/2 - self.controls.children[0].width*3/2, -self.controls.children[0].height*1.7
        self.container.size = (w, h)

    def on_touch_down(self, touches, touchID, x,y):
        lx,ly = super(MTInnerWindow, self).to_local(x,y)
        if self.controls.dispatch_event('on_touch_down', touches, touchID, lx, ly):
            return True
        return super(MTInnerWindow, self).on_touch_down( touches, touchID, x,y)

    def on_touch_move(self, touches, touchID, x,y):
        lx,ly = super(MTInnerWindow, self).to_local(x,y)
        if self.controls.dispatch_event('on_touch_move', touches, touchID, lx, ly):
            return True
        return super(MTInnerWindow, self).on_touch_move( touches, touchID, x,y)

    def on_touch_up(self, touches, touchID, x,y):
        lx,ly = super(MTInnerWindow, self).to_local(x,y)
        if self.controls.dispatch_event('on_touch_up', touches, touchID, lx, ly):
            return True
        return super(MTInnerWindow, self).on_touch_up( touches, touchID, x,y)

    def to_local(self,x,y):
        self.new_point = matrix_inv_mult(self.transform_mat, (x,y,0,1)) * self.get_scale_factor()
        return (self.new_point.x, self.new_point.y)

    def collide_point(self, x,y):
        scaled_border = self.border * (1.0/self.get_scale_factor())
        local_coords = super(MTInnerWindow,self).to_local(x,y)
        left, right = -scaled_border, self.width+scaled_border*2
        bottom,top = -scaled_border,self.height+scaled_border*2
        if local_coords[0] > left and local_coords[0] < right \
           and local_coords[1] > bottom and local_coords[1] < top:
            return True
        else:
            return False

    def draw(self):
        set_color(*self.color)
        scaled_border = self.border * (1.0/self.get_scale_factor())
        drawRoundedRectangle((-scaled_border, -scaled_border), (self.width+scaled_border*2, self.height+scaled_border*2))
        drawRectangle(((self.width/2)-(scaled_border*2.5), -scaled_border), (scaled_border*5, -scaled_border*1.2))

    def on_draw(self):
        with gx_matrix:
            glMultMatrixf(self.transform_mat)

            self.draw()

            # enable stencil test
            glClearStencil(0)
            glClear(GL_STENCIL_BUFFER_BIT)
            glEnable(GL_STENCIL_TEST)
            glStencilFunc(GL_NEVER, 0x0, 0x0)
            glStencilOp(GL_INCR, GL_INCR, GL_INCR)
            drawRectangle((0, 0), size=self.size)

            # draw inner content
            glStencilFunc(GL_EQUAL, 0x1, 0x1)
            glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
            self.container.dispatch_event('on_draw')
            glDisable(GL_STENCIL_TEST)

            self.controls.dispatch_event('on_draw')



