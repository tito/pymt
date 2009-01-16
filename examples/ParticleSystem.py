from pymt import *
import random

class ParticleObject(MTWidget):
    def __init__(self, parent=None, pos=(0,0), size=(20,20), color=(1,1,1),
                 rotation=45, **kargs):
        MTWidget.__init__(self, parent)
        self.x, self.y = pos
        self.size = size
        self.opacity = 1		
        self.color = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), self.opacity)
        self.rotation = 0
        self.zoom = 1

    def animate(self):
        self.show()
        self.from_x = self.x
        self.from_y = self.y
        self.to_x = int(random.uniform(self.x-100, self.x+100))
        self.to_y = int(random.uniform(self.y-100, self.y+100))
        self.length = random.uniform(0.2, 1.0)
        self.timestep = 1.0/60
        self.frame = 0

    def advance_frame(self, dt):
        self.frame += self.timestep
        self.x = AnimationAlpha.ramp(self.from_x, self.to_x, self.length, self.frame)
        self.y = AnimationAlpha.ramp(self.from_y, self.to_y, self.length, self.frame)
        self.rotation = AnimationAlpha.ramp(0, 360, self.length, self.frame)
        self.zoom = AnimationAlpha.ramp(1, 0, self.length, self.frame)
        self.opacity = AnimationAlpha.ramp(1, 0, self.length, self.frame)
        if self.frame >= self.length:
            self.hide()

    def draw(self):
        if not self.visible:
            return
        drawRectangle((self.x, self.y), self.size)

    def on_draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotated(self.rotation, 0,0,1)
        glScalef(self.zoom, self.zoom, 1)
        glTranslatef(-self.x, -self.y, 0)
        glTranslatef(-self.size[0]/2, -self.size[1]/2, 0)
        glColor4f(*self.color)		
        self.draw()
        glPopMatrix()

    def on_animation_complete(self, anim):
        self.hide()

class ParticleEngine(MTWidget):
    def __init__(self, parent=None, max=150, **kargs):
        MTWidget.__init__(self,parent,**kargs)

        print 'Particle Engine Initialized'
        self.max        = max
        self.particles  = {}
        for i in range(self.max):
            self.particles[i] = ParticleObject()
            self.particles[i].hide()
            self.add_widget(self.particles[i])

        pyglet.clock.schedule_once(self.advance_frame, 1/60.0)

    def draw(self):
        enable_blending()
        MTWidget.draw(self)

    def generate(self, pos, count):
        for i in range(self.max):
            if self.particles[i].visible:
                continue
            count = count - 1
            if count <= 0:
                return
            self.particles[i].x, self.particles[i].y = pos
            self.particles[i].animate()

    def advance_frame(self, dt):
        for i in range(self.max):
            if self.particles[i].visible:
                self.particles[i].advance_frame(dt)
        pyglet.clock.schedule_once(self.advance_frame, 1/60.0)

class ParticleShow(MTWindow):
    def __init__(self):
        MTWindow.__init__(self)
        self.pe = ParticleEngine()
        self.add_widget(self.pe)

    def on_touch_down(self, touches, touchID, x,y):
        print 'Background Touched'
        self.pe.generate((x, y), 30)
        return True

    def on_touch_move(self, touches, touchID, x,y):
        print 'Background Touched'
        self.pe.generate((x, y), 30)
        return True

#start the application (inits and shows all windows)
if __name__ == '__main__':
    w = ParticleShow()
    w.set_fullscreen()
    runTouchApp()