#PyGE_touch from kaswy
#Website http://kaswy.free.fr
#Depend of PyMT from  Thomas Hansen

from pymt import *
import pyglet

from math import sqrt
import win32com.client
import time

touchPositions = {}

class GEcamera:
	"Definition de camera GE"
	def __init__(self):
    		self.lat =1.0
		self.lon =1.0
		self.alt =10000000.0
		self.altMode =1
		self.rnge =0
		self.tilt =0
		self.azimuth =0.
		self.speed =5
		self.accx = 0.
		self.accy = 0.
	def set(self,dt):
		if len(touchPositions) == 0:
			self.lon -= self.accx
			self.accx = self.accx/1.1
			self.lat -= self.accy
			self.accy = self.accy/1.1
		#if self.azimuth > 45:self.azimuth = 45
		#if self.azimuth < -45:self.azimuth = -45
		if self.tilt > 90:self.tilt = 90
		if self.tilt < 0:self.tilt = 0
		if self.lon > 180:self.lon = -180
		if self.lon < -180:self.lon = 180
		if self.lat > 90:self.lat = 89.99999
		if self.lat < -90:self.lat = -90
		googleEarth.SetCameraParams(self.lat, self.lon, self.alt, self.altMode,self.rnge, self.tilt, self.azimuth, self.speed)


class Touch(TouchEventLoop):
    def __init__(self, config=None):
        global touch_event_listeners
        self.register_event_type('on_touch_up')
        self.register_event_type('on_touch_move')
        self.register_event_type('on_touch_down')
        touch_event_listeners.append(self)
        self.width=320
        self.height=240

    def on_touch_down(self, touches, touchID, x, y):
        pass
    def on_touch_move(self, touches, touchID, x, y):
        pass
    def on_touch_up(self, touches, touchID, x, y):
        pass

cam=GEcamera()
w=Touch()

@w.event
def on_touch_down(touches, touchID, x,y):
	touchPositions[touchID] = [(x,y)]
@w.event
def on_touch_up(touches, touchID,x,y):
	del touchPositions[touchID]
@w.event
def on_touch_move(touches, touchID, x, y):
	doigts = 0
	for p in touchPositions:
		doigts +=1
	if doigts == 1:
		#print "move"
		x0,y0 = touchPositions[touchID][0]
		cam.accx = (cam.accx + (x-x0)*(cam.alt/30000000))/2	# acceleration pour inertie
		cam.lon -= cam.accx
		cam.accy = (cam.accy + (y-y0)*(cam.alt/30000000))/2	# acceleration pour inertie
		cam.lat -= cam.accy
	if doigts == 2:
		#print "zoom"
		i=0
		for p in touchPositions:
			if p == touchID:
				x1,y1 = touchPositions[p][0]
			else:
				x2,y2 = touchPositions[p][0]
		cam.alt += (sqrt(abs((x2-x1)**2 + (y2-y1)**2))-sqrt(abs((x2-x)**2 + (y2-y)**2)))*cam.alt/100
		cam.accx = cam.accy = 0
	if doigts == 3:
		#print "tilt"
		for p in touchPositions:
			x3,y3 = touchPositions[p][0]
			if p == touchID:
				cam.tilt += (y3-y)/2
	touchPositions[touchID] = [(x,y)]



googleEarth =  win32com.client.Dispatch("GoogleEarth.ApplicationGE")
while not googleEarth.IsInitialized():
	print "waiting for Google Earth to initialize"
print "\n"
print "\n"
print "PyGE_touch Google Earth Navigator"
print "Only work on windows (there is no GE API in Linux)"
print "Depend on PyMT and Win32com modules"
print "\n"
print "One finger to move"
print "Two finger to zoom"
print "three finger to tilt"
print  "\n"
print "Have fun !!!!!!!!!"
getClock().schedule_interval(cam.set,0.01)
runTouchApp()


