from pymt import *
import pyglet



c = Container()
#c.add_widget( DragableObject(pos=(100,100)) )

for i in range (20):
		img_src = 'bilder/testpic'+str(i+1)+'.jpg'
		b = TestImageButton(img_src, parent=c, size=(0.16,0.16), pos = (i/5*300+150,i%5 * 200 + 100))
		b.status = 'not zoomed'
		
		anim = b.add_animation('zoom','x', 400, 1.0/60, 1)
		anim = b.add_animation('zoom','y', 400, 1.0/60, 1)
		anim = b.add_animation('zoom','scale', 0.6, 1.0/60, 1)
		
		anim = b.add_animation('shrink','x', i/5*300+150, 1.0/60, 1)
		anim = b.add_animation('shrink','y', i%5 * 200 + 100, 1.0/60, 1)
		anim = b.add_animation('shrink','scale', 0.16, 1.0/60, 1)
		
		def click(w):
			if w.status == 'zoomed':
				w.start_animations('shrink')
				w.status = 'not_zoomed'
			else:
				w.parent.widgets.remove(w)
				w.parent.widgest.append(w)
				w.start_animations('zoom')
				w.status = 'zoomed'		
				
		b.clickActions.append(  curry(click,b)  )
		c.add_widget(b)
		



w = UIWindow(c)
w.set_fullscreen()
runTouchApp()
