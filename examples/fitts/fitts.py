from pymt import *
import pyglet



c = Container()
#c.add_widget( DragableObject(pos=(100,100)) )


def curry(fn, *cargs, **ckwargs):
	def call_fn(*fargs, **fkwargs):
		d = ckwargs.copy()
		d.update(fkwargs)
		return fn(*(cargs + fargs), **d)
	return call_fn

for i in range (5):
	for j in range (5):
		if i*5+j+1 >= 25:
			break
		b = ImageButton('bilder/testpic'+str(i*5+j +1)+'.jpg',parent=c, pos=(i* 300+300,j*200+200)) 
		def myzoom(w):
			if w.target_scale < 1.0:
				w.setBig()
				w.parent.widgets.append(w)
				w.parent.widgets.remove(w)
			else:
				w.setSmall()
	
		b.clickActions.append(curry(myzoom, b))
		c.add_widget( b )






w = UIWindow(c)
w.set_fullscreen()
runTouchApp()
