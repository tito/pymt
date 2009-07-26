from __future__ import with_statement
from pymt import *
import os

class Workspace(MTScatterPlane):
    def __init__(self, **kwargs):
        super(Workspace,self).__init__( **kwargs)
        self.modules = [Module(filename = 'sl-addSynth+.svg'),
                        Module(filename = 'sl-speaker.svg'),
                        Module(filename = 'sl-distort+.svg')]
        for m in self.modules:
            self.add_widget(m)
        
class Module(MTSvg):
    def __init__(self, **kwargs):
        super(Module,self).__init__(**kwargs)
        self.touchstarts = [] # only react to touch input that originated on this widget
        self.mode = 'move'
        self.drag_x = 0
        self.drag_y = 0
        self.connected_modules = []
        
    def draw(self):
        if self.mode == 'draw_connection':
            set_color(1,1,1,1)
            drawLine([self.x + self.width / 2, self.y,self.drag_x,self.drag_y], width = 1)
        set_color(1,1,1,1)
        for module in self.connected_modules:
            drawLine([self.x + self.width / 2, self.y, module.x + self.width / 2 , module.y + module.height], width = 1)
        super(Module, self).draw()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x,touch.y):
            self.touchstarts.append(touch.id)
            self.first_x = touch.x
            self.first_y = touch.y
            self.first_pos_x = self.x
            self.first_pos_y = self.y
            if touch.y < self.y + 20:
                self.mode = 'draw_connection'
                self.drag_x = touch.x
                self.drag_y = touch.y
            else:
                self.mode = 'move'
            return True
        
    def on_touch_move(self, touch):
        if touch.id in self.touchstarts:
            delta_x = touch.x - self.first_x
            delta_y = touch.y - self.first_y
            if self.mode == 'move':
                self.x = self.first_pos_x + delta_x
                self.y = self.first_pos_y + delta_y
            if self.mode == 'draw_connection':
                self.drag_x = touch.x
                self.drag_y = touch.y
            return True
            
    def on_touch_up(self, touch):
        if self.mode == 'draw_connection':
            for m in self.parent.modules:
                if m.collide_point(touch.x,touch.y) and m != self:
                    self.connected_modules.append(m)
                    print m.filename
           
        if touch.id in self.touchstarts:
            self.touchstarts.remove(touch.id)
            self.mode = 'move'
            return True


workspace = Workspace(do_rotation = False)

w = MTWindow(style = {'bg-color': (0,0,0,1)})
w.add_widget(workspace)

runTouchApp()
