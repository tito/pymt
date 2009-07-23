from __future__ import with_statement
from pymt import *

class Line(MTWidget):
    def __init__(self, **kwargs):
        super(Line,self).__init__(**kwargs)
        
    def draw(self):
        set_color(1,1,1,1)
        drawLine([0,0,500,500], width = 5)
 
class Workspace(MTScatterPlane):
    def __init__(self, **kwargs):
        super(Workspace,self).__init__( **kwargs)

class LabIcon(MTSvg):
    def __init__(self, **kwargs):
        super(LabIcon,self).__init__(**kwargs)
        self.touchstarts = [] # only react to touch input that originated on this widget
        self.mode = 'move'
        
    #def draw(self):
        #super(LabIcon, self).draw()
        #with gx_matrix:
            #drawLine([0,0,500,500])
 
    def on_touch_down(self, touch):
        if self.collide_point(touch.x,touch.y):
            self.touchstarts.append(touch.id)
            self.first_x = touch.x
            self.first_y = touch.y
            self.first_pos_x = self.x
            self.first_pos_y = self.y
            self.first_width = self.width
            return True
        
    def on_touch_move(self, touch):
        if touch.id in self.touchstarts:
            delta_x = touch.x - self.first_x
            delta_y = touch.y - self.first_y
            if self.mode == 'move':
                self.x = self.first_pos_x + delta_x
                self.y = self.first_pos_y + delta_y
            return True
            
    def on_touch_up(self, touch):
        if touch.id in self.touchstarts:
            self.touchstarts.remove(touch.id)
            self.mode = 'move'
            return True


ws = Workspace(do_rotation = False)
s = LabIcon(filename = 'sl-addSynth+.svg')
s2 = LabIcon(filename = 'sl-speaker.svg')
w = MTWindow(style = {'bg-color': (0,0,0,1)})
ws.add_widget(s)
ws.add_widget(s2)
l = Line()
ws.add_widget(l)
w.add_widget(ws)

runTouchApp()
