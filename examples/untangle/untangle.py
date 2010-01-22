from __future__ import with_statement

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Untangle Game'
PLUGIN_AUTHOR = 'Thomas Hansen'
PLUGIN_EMAIL = 'thomas.hansen@gmail.com'
PLUGIN_DESCRIPTION = 'Untangle game !'

from pymt import *
from graph import *
from OpenGL.GL import *
from OpenGL.GLU import *

import time
import pickle

"""
I use the EventLogger and TrialLogger classes to record all the touch input, so that I can visualize/analyze the user interacitons for some user studies I am working on.
They have absolutly nothing to do with the Graph untabgle game, i case anyone is trying to read this to learn pymt.
"""
class EventLogger(MTWidget):
    def __init__(self):
        MTWidget.__init__(self)
        self.touches = {}
        self.enabled = False


    def start(self):
        self.enabled = True
        self.start_time = time.time()

    def stop(self):
        self.enabled = False
        self.stop_time = time.time()

    def clear(self):
        self.touches = {}

    def on_touch_down(self, touch):
        if self.enabled:
            event = {'type':'down', 'id':touch.id, 'x':touch.x, 'y':touch.y, 't':time.time() }
            self.touches[touch.id] = [event,]

    def on_touch_up(self, touch):
        if self.enabled and touch.id in self.touches:
            event = {'type':'up', 'id':touch.id, 'x':touch.x, 'y':touch.y, 't':time.time() }
            self.touches[touch.id].append(event)

    def on_touch_move(self, touch):
        if self.enabled and touch.id in self.touches:
            event = {'type':'move', 'id':touch.id, 'x':touch.x, 'y':touch.y, 't':time.time() }
            self.touches[touch.id].append(event)


class TrialLogger(EventLogger):
    def __init__(self, widget):
        EventLogger.__init__(self)
        self.widget = widget
        widget.parent.add_widget(self)
        self.widget_start = None


    def start(self):
        self.graph_start = pickle.dumps([self.widget.g.verts, self.widget.g.edges])
        self.start_time = time.time()
        self.enabled = True



    def save(self,filename):
        self.stop()
        self.graph_stop = pickle.dumps([self.widget.g.verts, self.widget.g.edges])
        self.stop_time = time.time()
        f = open(filename,'wb')
        data = {
            'graph_start' : self.graph_start,
            'graph_stop' : self.graph_stop,
                        'start_time': self.start_time,
                        'stop_time': self.stop_time,
            'touch_event_log': self.touches,
            }
        pickle.dump(data, f)
        f.close()


class NewGameMenu(MTBoxLayout):
    def __init__(self, window, **kwargs):
        super(NewGameMenu, self).__init__(**kwargs)
        self.window = window
        self.trial_num = 0

        b1 = MTButton(label="10 Vertices", size=(200,100))
        b1.push_handlers(on_release=curry(self.startNewGame, 10))
        self.add_widget(b1)

        b1 = MTButton(label="15 Vertices", size=(200,100))
        b1.push_handlers(on_release=curry(self.startNewGame, 15))
        self.add_widget(b1)

        b1 = MTButton(label="20 Vertices", size=(200,100))
        b1.push_handlers(on_release=curry(self.startNewGame, 20))
        self.add_widget(b1)

        b1 = MTButton(label="25 Vertices", size=(200,100))
        b1.push_handlers(on_release=curry(self.startNewGame, 25))
        self.add_widget(b1)

        self.graph = None
        self.start_time = None
        self.stop_time = None

    def on_update(self):
        self.center = self.get_parent_window().center

    def draw(self):
        if self.start_time and self.stop_time:
            set_color(0,0,0,0.5)
            drawRectangle(size=self.window.size)

            duration = str(self.stop_time - self.start_time)[:4] + " sec"
            glColor4f(0.5,1,0.5,1)
            drawLabel("Untangled!", pos=(self.x+425, self.y+240), font_size=64)
            glColor4f(0.7,0.7,0.7,1)
            drawLabel("time: "+duration+"  moves: "+str(self.num_moves), pos=(self.x+425, self.y+150), font_size=50)

    def startNewGame(self, numVerts, *largs):
        if self.graph:
            self.window.remove_widget(self.graph)
        self.graph = GraphUI(size=numVerts, w=self.window, menu=self)

        self.window.add_widget(self.graph)

        self.trial_num += 1
        self.log = TrialLogger(self.graph)
        self.log.start()

        self.window.remove_widget(self)
        self.start_time = time.time()


class GraphUI(MTWidget):
    def __init__(self, size=15, w=None, menu=None):
        MTWidget.__init__(self)
        self.menu = menu
        self.g = Graph(size,displaySize=w.size)
        self.touch2vertex = {}
        self.num_moves = 0
        self.done = False
        self.num_moves_since_check = 0 #if we try to solve on every move event things get slow

    def draw(self):
        self.g.draw()
        if not self.done:
            w = self.get_parent_window()
            glColor4f(0.7,0.7,0.7,1)
            duration = time.time() - self.menu.start_time
            label = 'Time: %4.1f - Moves: %d' % (duration, self.num_moves)
            drawLabel(label, pos=(w.center[0], 30), font_size=30)

    def on_touch_down(self, touch):
        if self.done:
            return
        touchedVertex = self.g.collideVerts(touch.x,touch.y)
        if touchedVertex: self.touch2vertex[touch.id] = touchedVertex

    def on_touch_up(self, touch):
        if self.done:
            return
        self.num_moves +=1
        if self.touch2vertex.has_key(touch.id):
            del self.touch2vertex[touch.id]
        if self.g.is_solved():
            #self.g = Graph(15,displaySize=w.size)
            self.done = True
            self.menu.log.stop()
            self.menu.log.save('trial_'+str(self.menu.trial_num)+'.pkl')
            self.menu.stop_time =  time.time()
            self.menu.num_moves = self.num_moves
            self.parent.add_widget(self.menu)

    def on_touch_move(self, touch):
        if self.done:
            return
        if self.touch2vertex.has_key(touch.id):
                    self.touch2vertex[touch.id][0] = touch.x
                    self.touch2vertex[touch.id][1] = touch.y
        self.num_moves_since_check += 1
        if self.num_moves_since_check%4 == 0:
            #self.g.is_solved()
            self.num_moves_since_check = 0


def pymt_plugin_activate(w, ctx):
    #ctx.log = TrialLogger(ctx.graph)
    ctx.menu = NewGameMenu(w, pos=(w.width/2 -425, w.height/2))
    w.add_widget(ctx.menu)

def pymt_plugin_deactivate(w, ctx):
    try:
        w.remove_widget(ctx.menu)
    except:
        pass
    #ctx.log.save('data.pkl')


if __name__ == '__main__':
    #init our window
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)

