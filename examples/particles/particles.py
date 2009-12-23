from __future__ import with_statement
from pymt import *
from OpenGL.GL import *
import random

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Particles Sandbox'
PLUGIN_AUTHOR = 'Sharath Patali & Mathieu Virbel'
PLUGIN_DESCRIPTION = 'All stars are coming under touches!'

class ParticleObject(MTWidget):
    def __init__(self, pos=(0,0), size=(20,20), color=(1,1,1),
            rotation=45, type='Squares', **kargs):
        MTWidget.__init__(self, pos=pos, size=size, color=color, **kargs)
        self.opacity = 0.5
        self.color = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), self.opacity)
        self.rotation = 0
        self.zoom = 1
        self._type = type
        self.dl = GlDisplayList()

    def _set_type(self, type):
        self._type = type
        self.dl.clear()
    def _get_type(self):
        return self._type
    type = property(_get_type, _set_type)
    
    def ramp(self, value_from, value_to, length, frame):
        return (1.0 - frame / length) * value_from  +  frame / length * value_to

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
        self.x = self.ramp(self.from_x, self.to_x, self.length, self.frame)
        self.y = self.ramp(self.from_y, self.to_y, self.length, self.frame)
        self.rotation = self.ramp(0, 360, self.length, self.frame)
        self.zoom = self.ramp(1, 0, self.length, self.frame)
        self.opacity = self.ramp(1, 0, self.length, self.frame)
        if self.frame >= self.length:
            self.hide()

    def draw(self):
        if not self.visible:
            return
        self.advance_frame(getFrameDt())
        if not self.dl.is_compiled():
            with self.dl:
                glColor4f(*self.color)
                if self.type == 'Squares':
                    drawRectangle(size=self.size)
                else:
                    drawCircle(radius=10)
        self.dl.draw()

    def on_draw(self):
        with gx_matrix:
            glTranslatef(self.x, self.y, 0)
            glRotated(self.rotation, 0,0,1)
            glScalef(self.zoom, self.zoom, 1)
            #glTranslatef(-self.size[0]/2, -self.size[1]/2, 0)
            self.draw()

class ParticleEngine(MTWidget):
    def __init__(self, max=500, **kargs):
        MTWidget.__init__(self, **kargs)
        #print 'Particle Engine Initialized'
        self.max        = max
        self.particles  = {}
        for i in range(self.max):
            self.particles[i] = ParticleObject()
            self.particles[i].hide()
            self.add_widget(self.particles[i])

    def on_draw(self):
        with gx_blending:
            super(ParticleEngine, self).on_draw()

    def set_type(self, type):
        for i in range(self.max):
            self.particles[i].type = type

    def generate(self, pos, count):
        for i in range(self.max):
            if self.particles[i].visible:
                continue
            count = count - 1
            if count <= 0:
                return
            self.particles[i].x, self.particles[i].y = pos
            self.particles[i].animate()

class ParticleShow(MTWidget):
    def __init__(self, pos=(0, 0), size=(100, 100), color=(0.6, 0.6, 0.6, 1.0),
                 pe=None, **kargs):
        MTWidget.__init__(self, pos=(0,0), size=(1440,900), color=(0,0,0,0), **kargs)
        self.pe = pe

    def on_touch_down(self, touch):
        self.pe.generate((touch.x, touch.y), 30)
        return True

    def on_touch_move(self, touch):
        self.pe.generate((touch.x, touch.y), 30)
        return True

    def on_touch_up(self, touch):
        return True

class SetButton(MTButton):
    def __init__(self, pos=(0, 0), size=(100, 100), label='Hello',
            pe=None, **kargs):
        MTButton.__init__(self, pos=pos, size=size, label=label, **kargs)
        self.label = label
        self.pe = pe

    def on_touch_down(self, touch):
        if self.collide_point(touch.x,touch.y):
            self.state = ('down', touch.id)
            if self.label == 'Squares':
                self.pe.set_type('Squares')
            else:
                self.pe.set_type('Circles')
            return True

def pymt_plugin_activate(w, ctx):
    ctx.pe = ParticleEngine()
    w.add_widget(ctx.pe)
    ctx.back = ParticleShow(pe=ctx.pe)
    w.add_widget(ctx.back)
    ctx.but1 = SetButton(pos=(20,40),size=(80,50),label='Squares', pe=ctx.pe)
    w.add_widget(ctx.but1)
    ctx.but2 = SetButton(pos=(20,100),size=(80,50),label='Circles', pe=ctx.pe)
    w.add_widget(ctx.but2)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.but2)
    w.remove_widget(ctx.but1)
    w.remove_widget(ctx.pe)
    w.remove_widget(ctx.back)

#start the application (inits and shows all windows)
if __name__ == '__main__':
    w = MTWindow(color=(0,0,0,1))
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
