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
from button import MTImageButton, MTButton
from layout.boxlayout import MTBoxLayout

iconPath = os.path.join(os.path.dirname(pymt.__file__), 'data', 'icons', '')

class MTInnerWindowContainer(MTRectangularWidget):
    '''Container used to simulate a window for children of MTInnerWindow.

    .. note::
        Don't use this class directly !
    '''
    def __init__(self, **kwargs):
        super(MTInnerWindowContainer, self).__init__(**kwargs)

    def add_on_key_press(self, *largs, **kwargs):
        return self.parent.parent.get_parent_window().add_on_key_press(*largs, **kwargs)
    def remove_on_key_press(self, *largs, **kwargs):
        return self.parent.parent.get_parent_window().remove_on_key_press(*largs, **kwargs)
    def get_on_key_press(self, *largs, **kwargs):
        return self.parent.parent.get_parent_window().get_on_key_press(*largs, **kwargs)

    def add_on_text(self, *largs, **kwargs):
        return self.parent.parent.get_parent_window().add_on_text(*largs, **kwargs)
    def remove_on_text(self, *largs, **kwargs):
        return self.parent.parent.get_parent_window().remove_on_text(*largs, **kwargs)
    def get_on_text(self, *largs, **kwargs):
        return self.parent.parent.get_parent_window().get_on_text(*largs, **kwargs)

    def add_on_text_motion(self, *largs, **kwargs):
        return self.parent.parent.get_parent_window().add_on_text_motion(*largs, **kwargs)
    def remove_on_text_motion(self, *largs, **kwargs):
        return self.parent.parent.get_parent_window().remove_on_text_motion(*largs, **kwargs)
    def get_on_text_motion(self, *largs, **kwargs):
        return self.parent.parent.get_parent_window().get_on_text_motion(*largs, **kwargs)

    def add_on_text_motion_select(self, *largs, **kwargs):
        return self.parent.parent.get_parent_window().add_on_text_motion_select(*largs, **kwargs)
    def remove_on_text_motion_select(self, *largs, **kwargs):
        return self.parent.parent.get_parent_window().remove_on_text_motion_select(*largs, **kwargs)
    def get_on_text_motion_select(self, *largs, **kwargs):
        return self.parent.parent.get_parent_window().get_on_text_motion_select(*largs, **kwargs)


class MTInnerWindow(MTScatterWidget):
    '''InnerWindow are a wrapper to render an application inside another
    application, and work like a multitouch window manager. With innerwindow,
    you can move / rotate / fullscreen an application.

    Checkout the `desktop` example to check how it work !
    '''
    def __init__(self, **kargs):
        super(MTInnerWindow, self).__init__(**kargs)
        self.color=(1,1,1,0.5)
        self.border = 20
        self.__w = self.__h = 0
        self.container = MTInnerWindowContainer(pos=(0,0), size=self.size, style={'bg-color':(0,0,0)})
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

    def fullscreen(self, *largs, **kwargs):
        root_win = self.parent.get_parent_window()

        # save state for restore
        self.old_children = root_win.children
        self.old_size = self.size

        # set new children
        root_win.children = []
        root_win.add_widget(root_win.sim)
        root_win.add_widget(self.container)

        btn_unfullscreen = MTButton(pos=(root_win.width-50, root_win.height-50),
                                    size=(50,50), label='Back')
        btn_unfullscreen.push_handlers(on_release=self.unfullscreen)
        root_win.add_widget(btn_unfullscreen)
        self.size = root_win.size

    def unfullscreen(self, *largs, **kwargs):
        # restore old widget
        root_win = self.parent.get_parent_window()
        root_win.children = self.old_children

        # reset container parent
        self.container.parent = self

        # set old size
        self.size = self.old_size

    def close(self, touchID=None, x=0, y=0):
        self.parent.remove_widget(self)

    def add_widget(self, w):
        self.container.add_widget(w)

    def remove_widget(self, w):
        self.container.remove_widget(w)

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

    def to_local(self, x, y):
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



