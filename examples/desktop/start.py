from pymt import *














def gesture_add_default(gdb):
    # Circle
    g = gdb.str_to_gesture('eNqFkMtqw0AMRff6EXtTo8doHj+Qbgv+gJImJoSm8eCZQPP3HTlpodDHIJiFdO7VVX/M17c6HKZSL8sEj/c/I/T7TDB2pS7z61Q6yAz9KQv0PxLjOgbZGaeNy/PxXA3zhoVfsCebghyNSo26NoAQNjhwiI45iiJ7j5EVyti9W5usTc6JkGpyrDElTVBetn96EK+RBA43AyHvveNEgYJScgHK4aaNilG5GWBAkabu/xdfc5N+iScvLogX4eiS4qf4Q9uclJAdtmwtFbEzcauxq/NpWrbn3WQx/RoTvz+yK9xXeM7LvL/sqg2H1TS0g7RAjiOLqNhNhg+4A4YT')
    g.label = 'Circle'
    g.id = 'circle'
    gdb.add_gesture(g)

    # Up
    g = gdb.str_to_gesture('eNqdkE1qAzEMhfe6yMwmRvK/L5BuC3OAkiZmCE0zZuxAcvtYHndRaLuoMc9gv+9J8nhOj88i5pjLbY3w0s+EMJ4SwTTksi4fMQ+QJIyXpGD8kZiaDZJmzlQuLedrYcwy5n7BXtkFyTMVKvWoACHsdyhMCM5SQN3UKA95Gu78TrBHgVL3J1bvnYL8fvizCsk2lIL5q4T15K3yyigpScsAef5/ehudzJaOQiNK5TGYptrKHr7j9H676RbOexrKconr4XqMPKjlHMLvi/gfegtvaV1Ot2Nhs2Oz17VfbhfR1Whta7J4AhYuhrk=')
    g.label = 'Up'
    g.id = 'up'
    gdb.add_gesture(g)

    # NUI-wave
    g = gdb.str_to_gesture('eNqFkMtuwyAQRffzI/am1jwYBn6g3VbyB1RpYkVR0xjZRGr+vkCdRaU+EBIL7jmXoT+l23sejtOar8sET9uZEPpDIhi7NS/z27R2kBj6cxLofyTGFoPkKqeFS/PpkivmK2a/YM81BSlUKhbqVgBCeHzAAX2g4KOLXhFFAhKsY/dRA9QCyjFECYFYjGN05f5192cNcZtK4HjvEBMrEmRE51jYYD3e9eiUWY0IWRxZ+F/fhif90uNApCoSA2pgZcdxk+PgDAk9UTDPVqqbu+6xy/N5WnaX/VQH9U2D31f7h+0FL2mZD9d9rmGrYTM11tpIJuX1rpiHT145hrs=')
    g.label = 'NUI-wave'
    g.id = 'menu'
    gdb.add_gesture(g)

    #A (without cross-bar)
    g = gdb.str_to_gesture('eNqFkE1qw0AMhfe6iL2pkUbS/Fwg2RZ8gJImJoSm8eCZQHP7jkxSKPRnEMxC73vSU3/Kt/c6HKdSr8sE2/ufEfpDJhi7Upf5bSodZAf9OTP0PxLjKoMsxmnj8ny6VMO8YeEX7NlUkKNRqVG3BhDC5gkH9uwcxSiSokTEBGXsPqxPa1+FXGBO3qnXFIOH8rr7cwq5NRTD8TECMRCpFyZJiSOU48OcoorjgIGVmVD/N1+Tk36Zq8eQsK2o6h3b+qs5DqIxOO+Rg7AgOTFvq7Gr83ladpf9ZDG9iQm/P7Ir3Dd4yct8uO6riQNsqOVJxF5iy0Ka7CDDJ/cphc4=')
    g.label = 'A (no cross-bar)'
    g.id = 'contextmenu'
    gdb.add_gesture(g)


plugins = MTPlugins(plugin_paths=['..'])
plugins.search_plugins()

def action_close_menu(menu, w, args):
    menu.parent.remove_widget(menu)
    del menu

def action_launch_plugin(menu, w, args):
    name, plugin = args

    win = MTInnerWindow(size=(320,280))
    plugins.activate(plugin, win)
    menu.parent.add_widget(win)
    #win.pos = w.pos

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

    def on_touch_up(self, touches, touchID, x, y):
        if not self.collide_point(x, y):
            return
        if self.action:
            self.action(self.parent, self, self.args)

class MTMenu(HVLayout):
    def __init__(self, **kwargs):
        kwargs.setdefault('alignment', 'vertical')
        kwargs.setdefault('uniform_width', True)
        kwargs.setdefault('uniform_height', True)
        super(MTMenu, self).__init__(**kwargs)

        self.orig_x = self.x
        self.orig_y = self.y

        plist = plugins.list()
        while len(plist):
            name, plugin = plist.popitem()
            infos = plugins.get_infos(plugin)
            w = MTActionButton(label=infos.get('title'), color=self.color,
                    action=action_launch_plugin, args=[name, plugin])
            self.add_widget(w)

        self.add_widget(MTActionButton(
            label='Close menu', action=action_close_menu))

    def on_draw(self):
        # For all next operation, enable blending
        enable_blending()
        super(MTMenu, self).on_draw()

    def on_move(self, x, y):
        pass

    def on_layout(self):
        # center layout
        self.x = self.orig_x - self.content_width / 2
        self.y = self.orig_y - self.content_height / 2


class MTGestureDetector(MTGestureWidget):
    def __init__(self, gdb, **kwargs):
        super(MTGestureDetector, self).__init__(**kwargs)
        self.gdb = gdb

    def draw(self):
        drawLabel('Draw a nui-wave to show menu',
            pos=(10, 10), center=False, font_size=20)

    def on_gesture(self, gesture, x, y):
        try:
            score, best = self.gdb.find(gesture)
        except Exception, e:
            return

        if best.id == 'menu':
            menu = MTMenu(pos=(x, y), color=(.2, .2, .2, .5))
            self.parent.add_widget(menu)


if __name__ == '__main__':
    # Create and fill gesture database
    gdb = GestureDatabase()
    gesture_add_default(gdb)

    # Create background window
    w = MTWallpaperWindow(wallpaper='wallpaper.jpg', show_fps=True)
    w.set_fullscreen()
    g = MTGestureDetector(gdb)
    w.add_widget(g)

    runTouchApp()
