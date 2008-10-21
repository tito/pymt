from pymt import *

c = Container()

for i in range (20):
		img_src = 'bilder/testpic'+str(i+1)+'.jpg'
		x , y =  i/5*300+150, i%5*200+100
		b = ImageButton(img_src, parent=c, scale=0.2, pos = (x,y))
		b.status = 'not zoomed'
		
		anim = b.add_animation('zoom','x', 200, 1.0/60, .1)
		anim = b.add_animation('zoom','y', 200, 1.0/60, .1)
		anim = b.add_animation('zoom','scale', 1.0, 1.0/60, .1)
		
		anim = b.add_animation('shrink','x', x, 1.0/60, .1)
		anim = b.add_animation('shrink','y', y, 1.0/60, .1)
		anim = b.add_animation('shrink','scale', 0.3, 1.0/60, .1)
		
		def click(w):
			if w.status == 'zoomed':
				w.start_animations('shrink')
				w.status = 'not_zoomed'
				
			else:
				w.start_animations('zoom')
				w.status = 'zoomed'
				c.widgets.remove(w)
				c.widgets.append(w)
				
		c.add_widget(b)
		b.clickActions.append(  curry(click,b)  )
		
		
w = UIWindow(c)
w.set_fullscreen()
runTouchApp()
