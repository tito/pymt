from pymt import *

c = MTWidget()

for i in range (10):
		img_src = 'bilder/testpic'+str(i+1)+'.jpg'
		x , y =  i/5*300+150, i%5*200+100
		b = MTScatterImage(img_src, parent=c, pos=(x,y))
		c.add_widget(b)
		
		
w = MTWindow()
w.add_widget(c)
w.set_fullscreen()
runTouchApp()
