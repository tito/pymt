from pymt import *
from OpenGL.GL import *

import pickle
from pprint import *

class DataViewer(MTWidget):
    def __init__(self, datafile):
        MTWidget.__init__(self)
        f = open(datafile)
        self.data = pickle.load(f)
        f.close()
        

    def draw(self):
        glPushMatrix()
        #glScaled(0.5,0.5,1.0)
         
        first_t = self.data['start_time']
        last_t = self.data['stop_time']
        #print first_t, last_t
        
        time_frame = (first_t, last_t)
        
        for touchID in self.data['touch_event_log']:
            timekey = lambda x: x['t']

            
            p1 = (0,0)
            p2 = (0,0)
            last_pos = (0,0)
            
            starts_at = self.data['touch_event_log'][touchID][0]['t']
            ends_at = self.data['touch_event_log'][touchID][-1]['t']
            
            if not (starts_at > time_frame[0] and ends_at < time_frame[1]):
                print touchID, starts_at, ends_at, time_frame
                continue
            for e in self.data['touch_event_log'][touchID]:
                t = (e['t'] - first_t)/(last_t -first_t) 
                #print e['t']
                #tt = (e['t'] - self.data['touch_event_log'][touchID][0]['t'])/(self.data['touch_event_log'][touchID][-1]['t'] - self.data['touch_event_log'][touchID][0]['t'])
                #t = tt
                if e['type'] != 'down':
                    p2 = (e['x'], e['y'])
                    #glColor3d(0, tt, tt)
                    glColor3d(1-t, 1-t, t)
                    drawLine(p1 + p2, width=1)
                    p1 = (e['x'], e['y'])
                    
                    
                if e['type'] == 'down':
                    p1 = (e['x'], e['y'])
                    glColor3d(1-t, 1-t, t)
                    drawCircle(p1, radius=8)
                    last_pos = p1
                    
                if e['type'] == 'up':
                    glColor3d(1-t, 1-t, t)
                    angle = Vector.angle(Vector(*last_pos),Vector(0,1) )
                    glPushMatrix()
                    glTranslated(p1[0], p1[1], 0)
                    if p1[0] < last_pos[0]:
                        glRotated(-angle, 0,0,1)
                    else:
                        glRotated(angle, 0,0,1)
                    drawTriangle(pos=(0,0), w=10, h=15)
                    glPopMatrix()
        glPopMatrix()
        
w = MTWindow()
w.color=(0,0,0,0)
w.add_widget(DataViewer('touch_25.pkl'))
runTouchApp()
