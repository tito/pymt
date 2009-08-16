from __future__ import with_statement
from pymt import *
import os
import osc

class Workspace(MTScatterPlane):
    def __init__(self, **kwargs):
        super(Workspace,self).__init__( **kwargs)
        osc.init()
        self.modules = [Module(filename = 'sl-addSynth+.svg', category = 'source', instance = 1),
                        Module(filename = 'sl-addSynth+.svg', category = 'source', instance = 2),
                        Module(filename = 'sl-speaker.svg', category = 'output', instance = 1),
                        Module(filename = 'sl-distort+.svg', category = 'effect', instance = 1),
                        Module(filename = 'sl-lfo+.svg', category = 'controller', instance = 1)]
        for m in self.modules:
            self.add_widget(m)
        
class Module(MTSvg):
    def __init__(self, **kwargs):
        super(Module,self).__init__(**kwargs)
        self.category = kwargs.get('category')
        self.type = kwargs.get('type')
        self.instance = kwargs.get('instance')
        self.touchstarts = [] # only react to touch input that originated on this widget
        self.mode = 'move'
        self.drag_x = 0
        self.drag_y = 0
        self.control_connections = []
        self.signal_connections = []
        
    def draw(self):
        if self.mode == 'draw_connection':
            set_color(1,1,1,1)
            x1 = self.x + self.width / 2
            y1 = self.y + 1
            x2 = self.drag_x
            y2 = self.drag_y
            drawLine([x1, y1, x2, y2], width = 1)
        
        set_color(1,1,1,1)
        for module in self.control_connections:
            x1 = self.x + self.width / 2
            y1 = self.y + 1
            if module[0].category == 'source':
                x2 = module[0].x + 16 + (module[1] - 1) * 16
                y2 = module[0].y + module[0].height - 1
            if module[0].category == 'effect':
                x2 = module[0].x + module[0].width - 4
                y2 = module[0].y + module[0].height - 20 - (module[1] - 1) * 13
            drawLine([x1, y1, x2, y2], width = 1)
        
        for module in self.signal_connections:
            x1 = self.x + self.width / 2
            y1 = self.y + 2
            x2 = module[0].x + self.width / 2. 
            y2 = (module[0].y + module[0].height) - 1
            drawLine([x1, y1, x2, y2], width = 1)
        super(Module, self).draw()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x,touch.y):
            self.touchstarts.append(touch.id)
            self.first_x = touch.x
            self.first_y = touch.y
            self.first_pos_x = self.x
            self.first_pos_y = self.y
            if self.category is not 'output':
                # Lower section
                if touch.y < self.y + 20:
                    self.mode = 'draw_connection'
                    self.drag_x = touch.x
                    self.drag_y = touch.y
                # Middle section        
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
                if m.collide_point(touch.x,touch.y) and m != self and m.category != 'controller':
                    # Control connections
                    if self.category == 'controller' and m.category != 'output':
                        if m.category == 'source':
                            inlet_calc = int(round((touch.x - m.x) / ((m.width - 10) / 4.)))
                            if inlet_calc >= 1 and inlet_calc <= 4:
                                inlet = inlet_calc
                            else: inlet = None
                        if m.category == 'effect':
                            inlet_calc = int(round((m.height - (touch.y - m.y)) / (m.height / 5.)))
                            if inlet_calc >= 1 and inlet_calc <= 4:
                                inlet = inlet_calc
                            else: inlet = None
                        if inlet:
                            if [m, inlet] not in self.control_connections:
                                self.control_connections.append([m, inlet])
                                osc.sendMsg("/connect", [self.category, self.instance, m.category, m.instance, inlet], '127.0.0.1',4444)
                    # Signal connections
                    if self.category == 'source' or self.category == 'effect' and m.category != 'source':
                        inlet = 0
                        if [m, inlet] not in self.signal_connections:
                            self.signal_connections.append([m, inlet])
                            osc.sendMsg("/connect", [self.category, self.instance, m.category, m.instance], '127.0.0.1',4444)
                        
           
        if touch.id in self.touchstarts:
            self.touchstarts.remove(touch.id)
            self.mode = 'move'
            return True


workspace = Workspace(do_rotation = False, auto_bring_to_front = False)

w = MTWindow(style = {'bg-color': (0,0,0,1)})
w.add_widget(workspace)
#w.add_widget(MTSlider())

runTouchApp()
