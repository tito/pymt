# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Bubble Battle !'
PLUGIN_AUTHOR = 'Mathieu Virbel'
PLUGIN_DESCRIPTION = 'Fight the bubbles !!!!! ]:X'

from pymt import *
from OpenGL.GL import *
from random import random, randint

class Basic(MTWidget):
    def __init__(self, **kwargs):
        super(Basic, self).__init__(**kwargs)
        self.r = 30

class Enemy(Basic):
    def __init__(self, **kwargs):
        self.level = kwargs.get('level')
        super(Enemy, self).__init__(**kwargs)
        self.dx = self.level * (random() - 0.5) * 40
        self.dy = self.level * 25 + random() * self.level
        self.r = self.r - min(self.r - 1, random() * self.level)

    def draw(self):
        # backgroud
        set_color(.75, 0, 0, .5)
        drawCircle(pos=self.pos, radius=self.r)
        #border
        set_color(.90, 2, 2, .5)
        drawCircle(pos=self.pos, radius=self.r, linewidth=3)


class Barier(Basic):
    def __init__(self, **kwargs):
        super(Barier, self).__init__(**kwargs)
        self.lifetime = 3
        self.initial_lifetime = self.lifetime
        self.life = 1
        self.start = True
        self.label = MTLabel(font_size=20, font_bold=True, anchor_x='center',
                             anchor_y='center')

    def draw(self):
        # border
        linewidth = self.r - (self.lifetime / float(self.initial_lifetime) * (self.r))
        set_color(.4, .4, .75, .9)
        drawCircle(pos=self.pos, radius=self.r + 3, linewidth=linewidth + 3)
        # background
        set_color(0, 0, .75, .7)
        drawCircle(pos=self.pos, radius=self.r)
        # text
        self.label.label = str(int(self.life))
        self.label.pos = (self.pos[0]-self.label.width/2,self.pos[1]-self.label.height/2)
        self.label.draw()

    def animate(self, world):
        dt = getFrameDt()
        if self.start:
            oldlife = self.life
            self.life += dt * world.managrow
            d = int(self.life) - int(oldlife)
            if d > 0:
                if world.mana - world.manacost * d < 0:
                    self.life = oldlife
                    self.stop()
                else:
                    world.mana -= world.manacost * d
            if self.life > 5:
                self.stop()
            self.update_radius()
        else:
            self.lifetime -= dt
            if self.lifetime < 0:
                return
        return True

    def update_radius(self):
        self.r = self.life * 20

    def stop(self):
        self.start = False
        self.life = int(self.life)
        self.lifetime = self.life * self.lifetime
        self.initial_lifetime = self.lifetime
        self.update_radius()

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

    def reset(self):
        self.enemies = []
        self.bariers = {}
        self.score = 0
        self.mana = 100
        self.nextspawn = 0
        self.spawnspeed = 1
        self.regenspeed = 5
        self.managrow = 3
        self.manacost = 5
        self.collidescore = 20
        self.collidemanafactor = .5
        self.levelscore = 100
        self.level = 1
        self.highscore = 0
        self.isgameover = False
        self.alphalevel = 1

    def animate(self):
        w = self.get_parent_window()
        dt = getFrameDt()
        e_delete = []
        b_delete = []

        # background
        self.alphalevel -= getFrameDt() * 3

        # animate enemies
        for e in self.enemies:
            # enemy collide on barier
            for bid in self.bariers:
                b = self.bariers[bid]
                if Vector(e.center).distance(Vector(b.center)) > e.r + b.r:
                    continue
                # collide happen !
                e_delete.append(e)
                # remove one life from barier
                b.life -= 1
                if b.life < 1:
                    b_delete.append(bid)
                b.update_radius()
                # update score + mana
                self.score += self.collidescore
                self.mana += self.manacost * self.collidemanafactor

            # advance enemy
            e.x += e.dx * dt
            e.y -= e.dy * dt

            if e.x < e.r:
                if e.dx < 0:
                    e.dx = -e.dx
                e.x = e.r + e.dx * dt
            elif e.x > w.width - e.r:
                if e.dx > 0:
                    e.dx = -e.dx
                e.x = w.width - e.r + e.dx * dt


            # enemy fall under screen
            if e.y < e.r:
                e_delete.append(e)
                self.score -= 100 * self.level + self.collidescore

        # animate barier
        for bid in self.bariers:
            b = self.bariers[bid]
            if not b.animate(self):
                b_delete.append(bid)

        # delete objects
        for e in e_delete:
            if e in self.enemies:
                self.enemies.remove(e)
        for b in b_delete:
            if b in self.bariers:
                del self.bariers[b]

    def regen(self):
        self.mana += getFrameDt() * self.regenspeed
        if self.mana > 100:
            self.mana = 100

    def spawn(self):
        self.nextspawn -= (getFrameDt() * .5) * self.spawnspeed
        if self.nextspawn < 0:
            self.nextspawn = 1.
            w = self.get_parent_window()
            x = w.width * random()
            y = w.height + 20
            self.enemies.append(Enemy(pos=(x, y), level=self.level))

    def nextlevel(self):
        if self.score > self.highscore:
            self.highscore = self.score
        if self.score < 0:
            self.gameover()
        if self.score < self.levelscore:
            return
        self.level += 1
        self.levelscore = self.levelscore * 2
        self.spawnspeed += 1
        self.regenspeed += 1
        self.managrow += 1
        self.alphalevel = 1
        self.collidescore += 2

    def gameover(self):
        self.stop()
        if not self.isgameover:
            self.isgameover = True
            self.get_parent_window().add_widget(GameOver(world=self))

    def stop(self):
        self.spawnspeed = 0
        self.regenspeed = 0

    def on_touch_down(self, touch):
        if self.mana - self.manacost <= 0:
            return
        self.mana -= self.manacost
        self.bariers[touch.id] = Barier(pos=(touch.x, touch.y))

    def on_touch_move(self, touch):
        if not touch.id in self.bariers:
            return
        self.bariers[touch.id].pos = touch.x, touch.y

    def on_touch_up(self, touch):
        if not touch.id in self.bariers:
            return
        self.bariers[touch.id].stop()

    def draw(self):
        # game
        self.spawn()
        self.animate()
        self.regen()
        self.nextlevel()

        # background
        w = self.get_parent_window()
        if self.alphalevel > 0:
            set_color(1, .4, .4, self.alphalevel)
            drawRectangle(size=w.size)

        # enemies + bariers
        for e in reversed(self.enemies):
            e.draw()
        for bid in reversed(self.bariers.keys()):
            self.bariers[bid].draw()

        # ui score
        w2 = w.width / 2.
        s = self.score / float(self.levelscore)
        set_color(.5, 0, 0, .8)
        drawRectangle(pos=(20, 20), size=((w2-40) * s, 30))
        set_color(.8, .2, .2, .8)
        drawRectangle(pos=(20, 20), size=(w2-40, 30), style=GL_LINE_LOOP)

        # ui mana
        w = self.get_parent_window()
        set_color(.1, .1, .7, .7)
        drawRectangle(pos=(w2 + 20, 20), size=((w2-40) * self.mana / 100., 30))
        set_color(.4, .4, 1, .9)
        drawRectangle(pos=(w2 + 20, 20), size=(w2-40, 30), style=GL_LINE_LOOP)

        # score
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
