from __future__ import with_statement
import math
from pymt import *
from pyglet.gl import GL_LINE_STRIP, glColor4f, glVertex2f, GL_LINE_BIT, glLineWidth

plugins = MTPlugins(plugin_paths=['..'])
plugins.search_plugins()

def gesture_add_default(gdb):
    # Circle
    g = gdb.str_to_gesture('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')
    g.label = 'Circle'
    g.id = 'circle'
    gdb.add_gesture(g)

    #X up_letf, bottom_right, top_right, bottom_left
    g = gdb.str_to_gesture('eNq1VttqHFcQfJ8fkV4s+n75Afk1oA8Iji2EiWMt2jXEf+86x6udSXAySoTFgmB3Tk2fqq7qvv54+PrH6ebh/nj68nS/vD3/P9By/eHAy93V8fT0+Pv98Wo5yHL96aDL9Q9P3M3HloONc45zh8ePn0/jWIxj+Q/HfhlPLYcapxqnvuIA03JLN0rRaZqhWekmthzvrv4cP/Ny+4ZuwiLYQtLFODt9Of727l9fwjLvpMvD9zeIFCBYVCOSvHM5PpzB3UzIuqqjO6RtH3xenP0ZnCusxQyvyGZqXcEts7VbKqW6m19QeUzwfAanCGJyofakSK1N6Sqpms5NTYb3v6D0yT73z0GX2UnCF3TyjHZPJg7z0uYVXkyJ8D1ol3JT2YefospZVECwUOpojm5L7ZQVnQrNBLHxQUuV0D7zMmUV/1nwU1jJFb4S93dJUZCvaWf4wZt2ZZYwwxXmQbEPP5WVvsADldukS4XImGSFTxKXMjzhqqW+T71OZZUv6MrtClEzGbZlXdG5DHqjl6IotGOfGZ266qorqE0rZwdFzlQrM+IQA1cipWQQU/vgU1VdVTXqaoVLnQilV6zgMGiUE37wthdIqlNSXSWVZBBaicZQJAnpK7CnnrrRE2dhUAaniDES+//YNtW0VU3EAJrFuxGwhUToV5BiU01b1YTLxc1RdilC1hAmr4GfetoavlQYCSg+3CtktNszdCUcrCyiaKawfQ/Z1NNyL9iH0BAD9mxDDiSPebKHPfW0S/JKob7sptJw5F9vepww4pC9LRyktp+7PvX0S+4qIBBbYERdi3LDCQliBWOuNMHVuNEe9pTT10lqsLYaI0EUTW65Gn/YPTFMkYnerPuc+PcNYtXScV2sAKRu4bmdFkRIkxFj4RjgmKgvyBWfcvo6SjtYGd1YiKhEM24GNWH/QJcmVScumLyfLD4V9XWWGjcbo3a2wj7hm1nK/3mDialpbDzKSPJA1xhsIgKCN7OUqzFBysAgyM/eh5+yxsalTcHesCL4xbKCfl3hG50+8ixHr3Ptz4uYysZmliKriwkxQGh6uQy7kfYBf2IDSeQl9sDa92lMYWOTu6gQVSO4YJcxOjcb2OAbPoA6ngYR9tGnrrFJ3sZ64hLCWE6hYW+Wx7+15b6fcuqam0lqCjsSvAT2kZXb1dRDMGURcHiDIW/20aesqZtphwmH1TMZmwbyZLPD/HCrHp+7q9Pjp/und5/f32MHh1TT3H/947Gin2v49fD0+OHL+9N42JdbHz4eaT5gDWoD9+YbKhZUkQ==')
    g.label = 'X'
    g.id = 'close'
    gdb.add_gesture(g)







def action_close_menu(menu, w, args, *largs):
    menu.parent.remove_widget(menu)
    del menu

def action_close_all(menu, w, args):
    sys.exit()

def action_launch_plugin(menu, w, args, *largs):
    name, plugin = args

    pos = w.parent.to_parent(*w.pos)
    win = MTInnerWindow(size=(320,280), pos=pos)
    plugins.activate(plugin, win)
    menu.parent.add_widget(win)

    action_close_menu(menu, w, None)

class MTActionButton(MTButton):
    def __init__(self, **kwargs):
        kwargs.setdefault('action', None)
        kwargs.setdefault('args', None)
        super(MTActionButton, self).__init__(**kwargs)
        self.height = self.label_obj.content_height + 10
        self.width = self.label_obj.content_width + 10
        self.action = kwargs.get('action')
        self.args = kwargs.get('args')

    def on_touch_up(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return
        if self.action:
            self.action(self.parent, self, self.args)

class MTMenu(MTKineticList):
    def __init__(self, **kwargs):
        kwargs.setdefault('title', None)
        kwargs.setdefault('searchable', False)
        kwargs.setdefault('deletable', False)
        kwargs.setdefault('padding_x', 0)
        kwargs.setdefault('padding_y', 1)
        super(MTMenu, self).__init__(**kwargs)

        self.size = (180, 230)
        self.center = self.pos

        self.orig_x = self.x
        self.orig_y = self.y
        self.color = kwargs.get('color')

        w = MTKineticItem(label='Close Menu', size=(220, 30),
                          style={'font-size': 12, 'bg-color': (.2, .2, .2)})
        w.push_handlers(on_press=curry(action_close_menu,
            self, w, []))
        self.add_widget(w)

        plist = plugins.list()
        while len(plist):
            name, plugin = plist.popitem()
            infos = plugins.get_infos(plugin)
            w = MTKineticItem(label=infos.get('title'), size=(180, 30),
                              style={'font-size': 12})
            w.push_handlers(on_press=curry(action_launch_plugin,
                self, w, [name, plugin]))
            self.add_widget(w)

class MTGestureDetector(MTGestureWidget):
    def __init__(self, gdb, **kwargs):
        super(MTGestureDetector, self).__init__(**kwargs)
        self.gdb = gdb
        self.label = MTLabel(label='Draw a circle to make the menu appear',
                             font_size=24, bold=True, anchor_x='center')
        self.dt = 0
        self.inactivity = 0
        self.inactivity_timeout = 5

    def draw(self):
        if len(getAvailableTouchs()):
            self.inactivity = 0
            return
        self.inactivity += getFrameDt()
        if self.inactivity < self.inactivity_timeout:
            return
        alpha = (self.inactivity - self.inactivity_timeout) / 3.
        alpha = boundary(alpha, 0, 1.)

        w = self.get_parent_window()
        s2 = Vector(w.size) / 2.
        self.dt += getFrameDt() * 2

        step = math.pi / 20.
        radius = 50
        i = 0
        with DO(gx_attrib(GL_LINE_BIT), gx_blending):
            glLineWidth(3)
            with gx_begin(GL_LINE_STRIP):
                while i < math.pi * 2:
                    x, y = math.cos(self.dt - i) * radius, math.sin(self.dt - i) * radius
                    glColor4f(1, 1, 1, min(alpha, i / math.pi))
                    glVertex2f(x + s2.x, y + s2.y - 70)
                    i += step

            set_color(1, 1, 1, alpha)
            drawCircle(pos=(x + s2.x, y + s2.y - 70), radius=4)
            drawCircle(pos=(x + s2.x, y + s2.y - 70), radius=20, linewidth=2)

        self.label.pos = Vector(w.size) / 2.
        self.label.color = (.5, .5, .5, min(alpha, .5))
        self.label.draw()
        self.label.y += 1
        self.label.x -= 1
        self.label.color = (1, 1, 1, alpha)
        self.label.draw()

    def on_gesture(self, gesture, touch):
        print self.gdb.gesture_to_str(gesture)
        try:
            score, best = self.gdb.find(gesture, minscore=.5)
        except Exception, e:
            return

        if best.id == 'circle':
            angle = gesture.get_rigid_rotation(best)
            menu = MTMenu(pos=(touch.x, touch.y), color=(.2, .2, .2, .5), rotation=angle)
            self.parent.add_widget(menu)

        if best.id == 'close':
            menu = MTMenu(pos=(touch.x, touch.y), color=(.2, .2, .2, .5))
            self.parent.add_widget(menu)


if __name__ == '__main__':
    # Create and fill gesture database
    gdb = GestureDatabase()
    gesture_add_default(gdb)

    # Create background window
    w = MTWallpaperWindow(wallpaper='wallpaper.jpg',
                          position=MTWallpaperWindow.SCALE)
    g = MTGestureDetector(gdb)
    w.add_widget(g)

    runTouchApp()
