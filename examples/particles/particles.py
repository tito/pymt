from __future__ import with_statement
from pymt import *
from OpenGL.GL import *
import random
import math

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Particles Sandbox'
PLUGIN_AUTHOR = 'Sharath Patali & Mathieu Virbel'
PLUGIN_DESCRIPTION = 'All stars are coming under touches!'

class ParticleObject:
    def __init__(self, settings):
        self.x, self.y  = 0, 0
        self.opacity    = 1.
        self.visible    = False
        self.alpha_func = AnimationAlpha.linear
        self.from_x     = 0
        self.from_y     = 0
        self.to_x       = 0
        self.to_y       = 0
        self.lifetime   = 1
        self.frame      = 0
        self.settings   = settings
        self.random_color()

    def random_color(self):
        r_min, r_max = map(lambda x: x/255., self.settings.color_r)
        g_min, g_max = map(lambda x: x/255., self.settings.color_g)
        b_min, b_max = map(lambda x: x/255., self.settings.color_b)
        self.color      = [random.uniform(r_min, r_max),
                           random.uniform(g_min, g_max),
                           random.uniform(b_min, b_max),
                           self.opacity]

    def alpha(self, a, b):
        alpha = self.alpha_func(self.frame / self.lifetime)
        return a * (1-alpha) + b * alpha

    def ramp(self, value_from, value_to, length, frame):
        return (1.0 - frame / length) * value_from  +  frame / length * value_to

    def animate(self, **kwargs):
        pos = kwargs.get('pos')
        rs = random.random() * self.settings.dispersion_start
        re = random.random() * self.settings.dispersion_end
        d = random.random() * math.pi * 2
        self.x, self.y  = pos
        self.from_x     = self.x + math.cos(d) * rs
        self.from_y     = self.y + math.sin(d) * rs
        self.to_x       = self.x + math.cos(d) * re
        self.to_y       = self.y + math.sin(d) * re
        self.lifetime   = self.settings.lifetime
        self.alpha_func = self.settings.alpha
        self.frame      = 0
        self.visible    = True
        self.random_color()

    def update(self, dt):
        if self.frame > self.lifetime:
            self.visible = False
            return True
        progress = self.frame / self.lifetime
        self.frame      += dt
        self.x          = self.alpha(self.from_x, self.to_x)
        self.y          = self.alpha(self.from_y, self.to_y)

        alpha = self.settings.alpha_decrease / 100.
        if progress < alpha:
            self.opacity = 1
        else:
            self.opacity    = 1 - ((progress - alpha) * (1 / (1 - alpha)))
        self.visible    = True
        self.color[3]   = self.opacity


class ParticleEngine(MTWidget):
    def __init__(self, max=5000, **kwargs):
        super(ParticleEngine, self).__init__(**kwargs)
        self.max        = max
        self.particles  = []
        self.image      = Image('../particles/dot.png')

        # properties used by particles
        self.alpha      = AnimationAlpha.linear
        self.dispersion_start   = 10
        self.dispersion_end     = 200
        self.alpha_decrease = 10
        self.color_r    = [0, 255]
        self.color_g    = [0, 255]
        self.color_b    = [0, 255]
        self.lifetime   = 1
        self.number     = 20
        self.pointsize  = 10

        for i in range(self.max):
            self.particles.append(ParticleObject(self))

        self.create_ui()

    def create_ui(self):
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <MTBoxLayout id="'layout'" orientation="'vertical'" invert_y="True">
        <MTGridLayout cols="4">
            <MTLabel label="'Lifetime'" size="(200, 30)"/>
            <MTSlider id="'sl_lifetime'" min="1" max="10" value="1"
                orientation="'horizontal'" value_show="True" size="(200, 30)"/>
            <MTLabel label="'Alpha decrease'" size="(200, 30)"/>
            <MTSlider id="'sl_alpha_decrease'" min="1" max="100" value="40"
                orientation="'horizontal'" value_show="True" size="(200, 30)"/>
            <MTLabel label="'Start dispertion'" size="(200, 30)"/>
            <MTSlider id="'sl_dispersion_start'" min="10" max="500" value="10"
                orientation="'horizontal'" value_show="True" size="(200, 30)"/>
            <MTLabel label="'End dispertion'" size="(200, 30)"/>
            <MTSlider id="'sl_dispersion_end'" min="10" max="500" value="200"
                orientation="'horizontal'" value_show="True" size="(200, 30)"/>
            <MTLabel label="'Number'" size="(200, 30)"/>
            <MTSlider id="'sl_number'" min="5" max="100" value="20"
                orientation="'horizontal'" value_show="True" size="(200, 30)"/>
            <MTLabel label="'Size'" size="(200, 30)"/>
            <MTSlider id="'sl_pointsize'" min="1" max="50" value="10"
                orientation="'horizontal'" value_show="True" size="(200, 30)"/>
            <MTLabel label="'Color range'" size="(200, 30)"/>
            <MTBoundarySlider id="'sl_color_r'" min="0" max="255"
                value_min="100" value_max="255"
                orientation="'horizontal'" showtext="True" size="(200, 30)"/>
            <MTBoundarySlider id="'sl_color_g'" min="0" max="255"
                value_min="0" value_max="255"
                orientation="'horizontal'" showtext="True" size="(200, 30)"/>
            <MTBoundarySlider id="'sl_color_b'" min="0" max="255"
                value_min="0" value_max="255"
                orientation="'horizontal'" showtext="True" size="(200, 30)"/>
        </MTGridLayout>
        <MTGridLayout rows="1">
            <MTLabel label="'Animation'" size="(120, 30)"/>
            <MTButton id="'btn_linear'" label="'linear'" size="(100, 30)"/>
            <MTButton id="'btn_ease_in_bounce'" label="'in_bounce'" size="(80, 30)"/>
            <MTButton id="'btn_ease_out_bounce'" label="'out_bounce'" size="(80, 30)"/>
            <MTButton id="'btn_ease_in_cubic'" label="'in_cubic'" size="(80, 30)"/>
            <MTButton id="'btn_ease_out_cubic'" label="'out_cubic'" size="(80, 30)"/>
            <MTButton id="'btn_ease_in_elastic'" label="'in_elastic'" size="(80, 30)"/>
            <MTButton id="'btn_ease_out_elastic'" label="'out_elastic'" size="(80, 30)"/>
        </MTGridLayout>
        </MTBoxLayout>
        '''
        w = XMLWidget()
        w.loadString(xml)

        layout = getWidgetById('layout')
        corner = MTSidePanel(layout=layout)
        self.add_widget(corner)

        getWidgetById('sl_number').connect('on_value_change', self, 'number')
        getWidgetById('sl_dispersion_start').connect(
            'on_value_change', self, 'dispersion_start')
        getWidgetById('sl_dispersion_end').connect(
            'on_value_change', self, 'dispersion_end')
        getWidgetById('sl_lifetime').connect('on_value_change', self, 'lifetime')
        getWidgetById('sl_pointsize').connect('on_value_change', self, 'pointsize')
        getWidgetById('sl_alpha_decrease').connect(
            'on_value_change', self, 'alpha_decrease')
        getWidgetById('sl_color_r').connect('on_value_change', self, 'color_r')
        getWidgetById('sl_color_g').connect('on_value_change', self, 'color_g')
        getWidgetById('sl_color_b').connect('on_value_change', self, 'color_b')
        for x in ('linear', 'ease_in_bounce', 'ease_out_bounce',
                  'ease_in_cubic', 'ease_out_cubic',
                  'ease_in_elastic', 'ease_out_elastic'):
            getWidgetById('btn_%s' % x).connect('on_press',
                   curry(self._btn_alpha_change, x))

    def _btn_alpha_change(self, funcname, *largs):
        self.alpha = getattr(AnimationAlpha, funcname)
        return True

    def draw(self):
        dt = getFrameDt()
        glTexEnvf(GL_POINT_SPRITE_ARB, GL_COORD_REPLACE_ARB, GL_TRUE)
        blend = GlBlending(sfactor=GL_SRC_ALPHA, dfactor=GL_ONE)
        set_texture(self.image.texture)
        glPointSize(self.pointsize)
        with DO(blend,
                gx_enable(self.image.texture.target),
                gx_enable(GL_POINT_SPRITE_ARB),
                gx_begin(GL_POINTS)):
            for p in self.particles:
                if p.update(dt):
                    continue
                glColor4f(*p.color)
                glVertex2f(p.x, p.y)

        count = len([x for x in self.particles if x.visible])
        statusline = 'Particles: %4d/%4d' % (count, self.max)
        w = getWindow()
        drawLabel(statusline, pos=(10, w.height - 20), anchor_x='left')

    def generate(self, pos, count):
        for i in range(self.max):
            if self.particles[i].visible:
                continue
            count = count - 1
            if count <= 0:
                return
            self.particles[i].animate(pos=pos)

    def on_touch_down(self, touch):
        if super(ParticleEngine, self).on_touch_down(touch):
            return True
        self.generate((touch.x, touch.y), self.number)
        return True

    def on_touch_move(self, touch):
        if super(ParticleEngine, self).on_touch_move(touch):
            return True
        self.generate((touch.x, touch.y), self.number)
        return True


def pymt_plugin_activate(w, ctx):
    ctx.pe = ParticleEngine()
    w.add_widget(ctx.pe)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.pe)

#start the application (inits and shows all windows)
if __name__ == '__main__':
    w = MTWindow(color=(0,0,0,1))
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
