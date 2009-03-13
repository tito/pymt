from __future__ import with_statement

from pymt.ui.widgets import MTAnimatedMenu
from pymt import *
from pyglet.gl import *

class MenuTestApp(MTWidget):
    def __init__(self):
        MTWidget.__init__(self)
        
        self.menu = MTAnimatedMenu ({'Options': 
                                        {   'File' : 
                                            {
                                                'New': lambda: self.doStuff('Handle New'),
                                                'Open': lambda: self.doStuff('Handle Open'),
                                                'Close': lambda: self.doStuff('Handle Close')
                                            },
                                            'Edit' :
                                            {
                                                'Find': lambda: self.doStuff('Handle Find'),
                                                'Replace': lambda: self.doStuff ('Handle Replace')
                                            }
                                        }
                                    })
    def on_touch_down(self, touches, touchID, x,y):
        self.menu.handle ((x,y)) 
        
    def doStuff(self, x):
        print str(x)
    
    def on_touch_up(self, touches, touchID,x,y):
        pass

    def on_touch_move(self, touches, touchID, x, y):
        pass
    
    def drawBackground (self):
        pos =(0,0)
        size = self.get_parent_window().size
        glColor3f (1.0, 1.0, 1.0)
        with gx_begin(GL_QUADS):
            glColor3f (0, 0, 0)
            glVertex2f(pos[0], pos[1])
            glColor3f (0.05, 0, 0)
            glVertex2f(pos[0] + size[0], pos[1])
            glColor3f (0.1, 0, 0)
            glVertex2f(pos[0] + size[0], pos[1] + size[1])
            glColor3f (0.05, 0, 0)
            glVertex2f(pos[0], pos[1] + size[1])

    def draw(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        w.clear()

        self.drawBackground ();

        glPushMatrix()
        self.menu.draw()
        glPopMatrix()

w = MTWindow()
w.add_widget(MenuTestApp())

runTouchApp()
