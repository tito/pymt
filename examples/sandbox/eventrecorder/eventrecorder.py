from pymt import *
import copy,pickle, pyglet, time



class MTEventRecorder(MTWidget):
    ''' MTEventRecorder records touch events so that they can be played back by MTEventPlayer.
    '''

    def __init__(self,**kwargs):
        MTWidget.__init__(self,**kwargs)
        self.touches = {}
        self.is_recording = False


    def start(self):
        '''starts recording events'''
        self.is_recording = True
        self.start_time = time.time()


    def stop(self):
        '''stops teh recording'''
        if self.is_recording:
            self.is_recording = False
            self.stop_time = time.time()


    def clear(self):
        self.touches = {}


    def on_touch_down(self, touches, touchID, x,y):
        if self.is_recording:
            event = {'type':'on_touch_down', 'id':touchID, 'x':x, 'y':y, 't':time.time() }
            self.touches[touchID] = [event,]


    def on_touch_up(self, touches, touchID,x,y):
        if self.is_recording:
            event = {'type':'on_touch_up', 'id':touchID, 'x':x, 'y':y, 't':time.time() }
            self.touches[touchID].append(event)


    def on_touch_move(self, touches, touchID, x, y):
        if self.is_recording:
            event = {'type':'on_touch_move', 'id':touchID, 'x':x, 'y':y, 't':time.time() }
            self.touches[touchID].append(event)


    def save(self, filename):
        '''saves the event recorindg to a file for reading by EventPlayer'''
        self.stop()
        f = open(filename,'wb')
        data = [self.touches, (self.start_time, self.stop_time)]
        pickle.dump(data, f)
        f.close()


MTWidgetFactory.register('MTEventRecorder', MTEventRecorder)




#TODO: use start_time and stop_time to allow for setting poition in playback.
#TODO: figure out a way to allow reverse and forward playback..will need different approach
#      maybe use linked list style traversal to have current index for each touch
#TODO: integrate optional transformation of event coordinates by parent widget transform
#TODO: change this to generate new touchID's instead if using old ones
#      might require virtual/mouse touches to generate normal numbers as well
class MTEventPlayer(MTWidget):
    ''' MTEventPlayer plays back events recorded by MTEventRecorder.

    :Parameters:
        `speed` : float, default is 1.0
            speed at which events are played back (e.g: 0.5 = half speed, 2.0 = double speed )
            usefull for use in unit testing or going through long event recordings
        `update_interval` : float, default is 0.01
            interval in seconds at which events are updated/replayed (smallest time step between events)
    '''
    def __init__(self, **kwargs):
        MTWidget.__init__(self,**kwargs)
        kwargs.setdefault('speed', 1.0)
        kwargs.setdefault('update_interval', 0.01)

        self.t = 0.0
        self.events ={}
        self.events_playing = {}
        self.speed = kwargs['speed']
        self.update_interval = kwargs['update_interval']

        getClock().schedule_interval(self.update, self.update_interval)


    def load(self, filename):
        f = open(filename)
        data = pickle.load(f)
        f.close()
        self.events  = data[0]
        self.start_time, self.stop_time = data[1]
        self.restart()


    def restart(self):
      self.events_playing = copy.deepcopy(self.events)
      self.t = self.start_time


    def update(self, dt):
        for touch in self.events_playing:
            while len(self.events_playing[touch]) and self.events_playing[touch][0]['t'] <= self.t:
                event = self.events_playing[touch][0]
                if event['type'] == 'on_touch_down':
                   self.get_parent_window().dispatch_event('on_touch_down', [], touch, event['x'],event['y'])
                if event['type'] == 'on_touch_move':
                   self.get_parent_window().dispatch_event('on_touch_move', [], touch, event['x'],event['y'])
                if event['type'] == 'on_touch_up':
                   self.get_parent_window().dispatch_event('on_touch_up', [], touch, event['x'],event['y'])
                self.events_playing[touch].pop(0)
        self.t += (dt*self.speed)


MTWidgetFactory.register('MTEventPlayer', MTEventPlayer)






if __name__ =="__main__":
    xmldef = '''<?xml version="1.0" encoding="UTF-8"?>
    <MTWidget>
        <MTEventRecorder id="recorder" />
        <MTEventPlayer id="player" />
        <MTDisplay />
        <MTButton label="record" pos="(0,0)" color="(1,0,0)" id="rec_btn" />
        <MTButton label="'play'" pos="(100,0)" color="(0,1,0)" id="'play_btn'"/>
    </MTWidget>
    '''

    def record(touchID, x, y):
        recorder = getWidgetById('recorder')
        if recorder.is_recording:
            recorder.save('test.trec')
            getWidgetById('rec_btn').label = "record"
        else:
            recorder.start()
            getWidgetById('rec_btn').label = "stop"


    def play(touchID, x, y):
        getWidgetById('player').load('test.trec')


    w = MTWindow(fullscreen=False, vsync=False, width=720, height=500)
    w.add_widget(XMLWidget(xml=xmldef))
    getWidgetById('rec_btn').push_handlers(on_release=record)
    getWidgetById('play_btn').push_handlers(on_release=play)

    runTouchApp()
