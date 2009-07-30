#!/usr/bin/env python
#work in progress do not touch thanks. Flipo

from __future__ import with_statement
__all__ = ['MTTrajectory']

from pyglet.gl import *
from pymt.graphx import set_color, drawRectangle,drawRoundedRectangle, gx_matrix, GlDisplayList
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widgets.widget import MTWidget


class MTTrajectory(MTWidget):
    def __init__(self,**kwargs):
        super(MTTrajectory, self).__init__(**kwargs)
        self.trajectory_dict = {}
        self.trajectory_dict_compiled = {}
        self.close = True
        
    def draw(self):
        for trajectory in self.trajectory_dict:
            if trajectory in self.trajectory_dict_compiled:
                self.trajectory_dict_compiled[trajectory].draw()
            else:
                self.draw_trajectory(self.trajectory_dict[trajectory])                        
    
    def draw_trajectory(self, trajectory, close = False):
        for i in range(len(trajectory)):
            with gx_begin(GL_LINES):
                glVertex2f(trajectory[i][0], trajectory[i][1])
                if i < len(trajectory) - 1:
                    glVertex2f(trajectory[i+1][0], trajectory[i+1][1])
                if close:
                    glVertex2f(trajectory[0][0], trajectory[0][1])
                    glVertex2f(trajectory[len(trajectory)-1][0], trajectory[len(trajectory)-1][1])
    
    def on_touch_down(self, touch):
        self.trajectory_dict[touch.id] = []
            
    def on_touch_move(self, touch):
        self.trajectory_dict[touch.id].append((touch.x,touch.y))
    
    def on_touch_up(self, touch):
        self.trajectory_dict_compiled[touch.id] = GlDisplayList()
        with self.trajectory_dict_compiled[touch.id]:
            self.draw_trajectory(self.trajectory_dict[touch.id], self.close)

            
MTWidgetFactory.register('MTTrajectory', MTTrajectory)

if __name__ == '__main__':
    from pymt import *
    w = MTWindow()
    mms = MTTrajectory()
    w.add_widget(mms)
    runTouchApp()