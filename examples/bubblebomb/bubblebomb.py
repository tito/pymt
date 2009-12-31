# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Bubble-o-Bomb !'
PLUGIN_AUTHOR = 'Mathieu Virbel'
PLUGIN_DESCRIPTION = 'Secure Bubble Bomb before explosion !'

from pymt import *
from OpenGL.GL import *
from random import random, randint


class Bomb(MTWidget):
    def __init__(self, **kwargs):
        super(Bomb, self).__init__(**kwargs)
        self.r = 30
        self.moved = False
        self.speed = 200
        self.level = kwargs.get('level')
        self.dx, self.dy = map(lambda x: randint(-self.speed, self.speed), xrange(2))
        self.lifetime = 8
        self.initial_lifetime = self.lifetime
        self.life = 1
        self.start = True
        self.saved = False
        self.color = kwargs.get('color')
        self.label = MTLabel(font_size=20, font_bold=True, anchor_x='center',
                anchor_y='center')

    def draw(self):
        # border
        linewidth = self.r - (self.lifetime / float(self.initial_lifetime) * (self.r))
        if self.color == 'red':
            set_color(.75, .4, .4, .9)
        else:
            set_color(.4, .4, .75, .9)
        drawCircle(pos=self.pos, radius=self.r + 3, linewidth=linewidth + 3)
        # background
        if self.color == 'red':
            set_color(.75, 0, 0, .7)
        else:
            set_color(0, 0, .75, .7)
        drawCircle(pos=self.pos, radius=self.r)
        # text
        self.label.label = str(int(self.lifetime+1))
        self.label.pos = (self.pos[0]-self.label.width/2,self.pos[1]-self.label.height/2)
        self.label.draw()

    def animate(self, world):
        dt = getFrameDt()
        if self.saved:
            return True
        self.lifetime -= dt
        if self.lifetime < 0:
            return
        return True

class DropBase(MTWidget):
    def __init__(self, **kwargs):
        super(DropBase, self).__init__(**kwargs)
        self.r = 100
        self.color = kwargs.get('color')

    def draw(self):
        # border
        if self.color == 'red':
            set_color(.75, .4, .4, .7)
        else:
            set_color(.4, .4, .75, .7)
        drawCircle(pos=self.pos, radius=self.r + 3, linewidth=3)
        # background
        if self.color == 'red':
            set_color(.75, 0, 0, .7)
        else:
            set_color(0, 0, .75, .7)
        drawCircle(pos=self.pos, radius=self.r)

class GameOver(MTWidget):
    def __init__(self, **kwargs):
        self.world = kwargs.get('world')
        super(GameOver, self).__init__(**kwargs)
        self.layout = MTBoxLayout(orientation='vertical', uniform_width=True,
                                  uniform_height=True, padding=100,
                                  spacing=20, invert_y=True)
        k = {'font_size': 48}
        self.text = MTLabel(label='GAME OVER', **k)
        self.textlevel = MTLabel(label='Your level is %d' % self.world.level, **k)
        self.textscore = MTLabel(label='Your score is %d' % self.world.highscore, **k)
        self.restart = MTButton(label='Restart')
        self.layout.add_widget(self.text)
        self.layout.add_widget(self.textlevel)
        self.layout.add_widget(self.textscore)
        self.layout.add_widget(self.restart)
        self.restart.push_handlers(on_press=self.handle_restart)
        self.add_widget(self.layout)

    def handle_restart(self, *largs):
        self.world.reset()
        self.parent.remove_widget(self)

    def on_touch_down(self, touch):
        super(GameOver, self).on_touch_down(touch)
        return True

    def on_touch_move(self, touch):
        super(GameOver, self).on_touch_move(touch)
        return True

    def on_touch_up(self, touch):
        super(GameOver, self).on_touch_up(touch)
        return True

    def draw(self):
        w = self.get_parent_window()
        self.layout.x = (w.width - self.layout.width) / 2.
        self.layout.y = (w.height - self.layout.height) / 2.
        set_color(0.2, 0.2, 0.2, .5)
        drawRectangle(size=w.size)

class World(MTWidget):
    def __init__(self, **kwargs):
        super(World, self).__init__(**kwargs)
        self.reset()
        self.s_gameover = SoundLoader.load('../bubblebomb/gameover.wav')
        self.s_touch = SoundLoader.load('../bubblebomb/touch.wav')
        self.s_nextlevel = SoundLoader.load('../bubblebomb/level.wav')

    def sound(self, name):
        if name == 'gameover':
            self.s_gameover.play()
        elif name == 'touch':
            self.s_touch.play()
        elif name == 'nextlevel':
            self.s_nextlevel.play()

    def reset(self):
        self.bomb = []
        self.touches = {}
        self.score = 0
        self.nextspawn = 0
        self.spawnspeed = 1
        self.levelscore = 10
        self.level = 1
        self.highscore = 0
        self.isgameover = False
        self.alphalevel = 1
        self.bases = (DropBase(color='red'), DropBase(color='blue'))

    def animate(self):
        if self.isgameover:
            return

        w = self.get_parent_window()
        dt = getFrameDt()

        # background
        self.alphalevel -= getFrameDt() * 3

        # animate enemies
        for b in self.bomb:
            if not b.animate(self):
                self.gameover()

            for base in self.bases:
                if Vector(b.pos).distance(Vector(base.pos)) > b.r + base.r:
                    continue
                if not b.saved:
                    b.dx = - b.dx
                    b.dy = - b.dy
                    b.x += b.dx * dt
                    b.y -= b.dy * dt

            # advance enemy
            if b.moved:
                continue

            b.x += b.dx * dt
            b.y -= b.dy * dt

            if b.x < b.r:
                if b.dx < 0:
                    b.dx = -b.dx
                b.x = b.r + b.dx * dt
            elif b.x > w.width - b.r:
                if b.dx > 0:
                    b.dx = -b.dx
                b.x = w.width - b.r + b.dx * dt
            elif b.y < b.r:
                if b.dy > 0:
                    b.dy = -b.dy
                b.y = b.r + b.dy * dt
            elif b.y > w.height - b.r:
                if b.dy < 0:
                    b.dy = -b.dy
                b.y = w.height - b.r + b.dy * dt
            elif b.saved and Vector(b.pos).distance(b.savedbase.pos) >= b.savedbase.r - b.r:
                b.dx = - b.dx
                b.dy = - b.dy
                b.x += b.dx * dt
                b.y -= b.dy * dt

    def nextlevel(self):
        if self.score > self.highscore:
            self.highscore = self.score
        if self.score < 0:
            self.gameover()
        if self.score < self.levelscore:
            return
        self.sound('nextlevel')
        self.level += 1
        self.levelscore = self.levelscore * 2
        self.spawnspeed += .5
        self.alphalevel = 1
        b_delete = [b for b in self.bomb if b.saved]
        [self.bomb.remove(b) for b in b_delete if b in self.bomb]

    def spawn(self):
        self.nextspawn -= (getFrameDt() * .5) * self.spawnspeed
        if self.nextspawn < 0:
            c = ('red', 'blue')[randint(0, 1)]
            b = Bomb(color=c, level=self.level)
            self.nextspawn = 1.
            w = self.get_parent_window()
            redo = True
            while redo:
                x = w.width * random()
                y = w.height * random()
                redo = False
                for base in self.bases:
                    if Vector(base.pos).distance(Vector(x, y)) < base.r + b.r:
                        redo = True
            b.pos = x, y
            self.bomb.append(b)

    def gameover(self):
        self.stop()
        if not self.isgameover:
            self.sound('gameover')
            self.isgameover = True
            self.get_parent_window().add_widget(GameOver(world=self))

    def stop(self):
        self.spawnspeed = 0

    def on_touch_down(self, touch):
        # search a bomb
        for b in self.bomb:
            if b.saved:
                continue
            if Vector(b.pos).distance(Vector(touch.x, touch.y)) > b.r:
                continue
            self.sound('touch')
            self.touches[touch.id] = b
            b.pos = touch.x, touch.y
            b.moved = True
            touch.grab(self)
            return True

    def on_touch_move(self, touch):
        if touch.id not in self.touches:
            return
        self.touches[touch.id].pos = touch.x, touch.y
        return True

    def on_touch_up(self, touch):
        if touch.id not in self.touches:
            return
        self.touches[touch.id].pos = touch.x, touch.y
        b = self.touches[touch.id]
        b.moved = False
        for base in self.bases:
            if Vector(b.pos).distance(Vector(base.pos)) > b.r + base.r:
                continue
            if b.color != base.color:
                self.gameover()
                return
            elif not b.saved:
                self.sound('touch')
                self.score += 1
                b.saved = True
                b.savedbase = base
                b.pos = base.pos
                return True

    def draw(self):
        w = self.get_parent_window()
        step = w.width / (1+len(self.bases))
        x = step
        for b in self.bases:
            b.pos = x, w.height / 2
            x += step

        # game
        self.spawn()
        self.animate()
        self.nextlevel()

        # background
        if self.alphalevel > 0:
            set_color(1, .4, .4, self.alphalevel)
            drawRectangle(size=w.size)

        # enemies + bariers
        for b in reversed(self.bases):
            b.draw()
        for b in reversed(self.bomb):
            b.draw()

        # score
        w2 = w.width / 2.
        set_color(.5, .5, .5, .5)
        drawRoundedRectangle(pos=(w2/2, w.height - 35), size=(w2, 50))
        set_color(.5, .5, .5, .5)
        drawRoundedRectangle(pos=(w2/2, w.height - 35), size=(w2, 50), style=GL_LINE_LOOP)
        label = 'Level %d ~ Score: %-5d / %5d' % (self.level, self.score, self.levelscore)
        drawLabel(label=label, pos=(w2, w.height - 15), color=(255, 255, 255, 200))

def pymt_plugin_activate(w, ctx):
    ctx.c = World()
    w.add_widget(ctx.c)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.c)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
