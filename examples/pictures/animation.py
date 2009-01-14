from pymt import *
import random

c = MTWidget()

class MTScatteredObj(MTScatterImage):
	"""MTScatteredObj is a zoomable Image widget with a possibility of providing rotation during spawning"""
	def __init__(self, img_src,parent=None, pos=(0,0), size=(100,100), rotation=45):
		MTScatterImage.__init__(self,img_src,parent,pos,size)
		self.rotation = rotation

for i in range (10):
		img_src = 'bilder/testpic'+str(i+1)+'.jpg'
		x = random.randint(100, 1000)
		y = random.randint(100, 700)
		size = random.uniform(0.25, 4.1)*100
		rot = random.uniform(0, 360)
		b = MTScatteredObj(img_src, c, (x,y),(size,size), rot)
		c.add_widget(b)
		
		
w = MTWindow()
w.add_widget(c)
w.set_fullscreen()
runTouchApp()
