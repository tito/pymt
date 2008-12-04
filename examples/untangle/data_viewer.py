from pymt import *
from pyglet.gl import *

import pickle
from pprint import *

class DataViewer(Widget):
    def __init__(self, datafile):
        Widget.__init__(self)
        f = open(datafile)
        self.data = pickle.load(f)
        f.close()
        

    def draw(self):
        glPushMatrix()
        glScaled(0.5,0.5,1.0)
        
        
        sorted_t = sorted(self.data['events'].keys())
        
        first_t = self.data['events'][sorted_t[0]][0]['t']
        last_t = self.data['events'][sorted_t[-1]][-1]['t']
        #print first_t, last_t
        
        for touchID in self.data['events']:
            timekey = lambda x: x['t']

            
            p1 = (0,0)
            p2 = (0,0)
            for e in self.data['events'][touchID]:
                t = (e['t'] - first_t)/(last_t -first_t) /4.0
                #print e['t']
                tt = (e['t'] - self.data['events'][touchID][0]['t'])/(self.data['events'][touchID][-1]['t'] - self.data['events'][touchID][0]['t'])
                if e['type'] != 'down':
                    p2 = (e['x'], e['y'])
                    #glColor3d(0, tt, tt)
                    glColor3d(1, 1-t, 0)
                    drawLine(p1 + p2, width=1)
                    p1 = (e['x'], e['y'])
                    
                if e['type'] == 'down':
                    p1 = (e['x'], e['y'])
                    glColor3d(1, 1-t, 0)
                    drawCircle(p1, radius=10)
                    
                if e['type'] == 'up':
                    glColor3d(1, 1-t, 0)
                    drawCircle(p1, radius=10)
                    
        glPopMatrix()
        
w = UIWindow(DataViewer('single-mouse.pkl'))
runTouchApp()