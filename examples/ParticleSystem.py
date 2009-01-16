from pymt import *
import random

class particle(MTRectangularWidget):
    def __init__(self, parent, pos=(0, 0), size=(100, 100), color=(0, 0, 0, 1.0),rotation=45, **kargs):
        MTRectangularWidget.__init__(self,parent, pos, size, **kargs)
        self.x, self.y = pos
        self.width, self.height = size
        self.red = color[0]
        self.green = color[1]
        self.blue = color[2]		
        self.opacity = color[3]
        self.rotation = rotation
        self.zoom = 1.0

    def draw(self):
        enable_blending()	
        glColor4d(self.red,self.green,self.blue,self.opacity)
        drawRectangle((self.x, self.y), (self.width, self.height))
		
    def on_draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotated(self.rotation, 0,0,1)
        glScalef(self.zoom, self.zoom, 1)
        glTranslatef(-self.x, -self.y, 0)
        glTranslatef(-self.width/2, -self.height/2, 0)
        self.draw()
        glPopMatrix()
		
    def on_animation_complete(self, anim):
        self.parent.remove_widget(self)
        


class particleEngine(MTWidget):
    def __init__(self,parent,numParticles=0, origin=(500,400),**kargs):
        MTWidget.__init__(self,parent,**kargs)	
        print "Particle Engine Initialized"
        self.num_of_particles = numParticles
        self.originX = origin[0] 
        self.originY = origin[1]
		
    def generateParticles(self):
        for i in range(self.num_of_particles):
            #p = particle(None,(self.originX,self.originY),(25,25),(random.uniform(0, 1),random.uniform(0, 1),random.uniform(0, 1),1))
            p = particle(None,(self.originX,self.originY),(5,5),(1,1,1,1))
            xDir = int(random.uniform(self.originX-100, self.originX+100))
            yDir = int(random.uniform(self.originY-100, self.originY+100))
            plife = random.uniform(0.2, 0.25)
            anim = p.add_animation('rotScaleFade','x', xDir, 1.0/60, plife)
            anim = p.add_animation('rotScaleFade','y', yDir, 1.0/60, plife)
            anim = p.add_animation('rotScaleFade','rotation',360, 1.0/60, plife)
            anim = p.add_animation('rotScaleFade','zoom',0.0, 1.0/60, plife)
            anim = p.add_animation('rotScaleFade','opacity',0, 1.0/60, plife)		
            self.add_widget(p)		
            p.start_animations('rotScaleFade')
			
			
class ParticleShow(MTWindow):
	def on_touch_down(self, touches, touchID, x,y):
			print "Background Touched"
			pe = particleEngine(self,5,(x,y))
			w.add_widget(pe)
			pe.generateParticles()
			return True
	
	def on_touch_move(self, touches, touchID, x,y):
			print "Background Touched"
			pe = particleEngine(self,5,(x,y))
			w.add_widget(pe)
			pe.generateParticles()
			return True
			
#start the application (inits and shows all windows)
if __name__ == '__main__':
	w = ParticleShow()
	#w.set_fullscreen()
	pe = particleEngine(None,50)
	w.add_widget(pe)
	pe.generateParticles()
	

	runTouchApp()
