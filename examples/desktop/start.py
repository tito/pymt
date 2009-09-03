from __future__ import with_statement
import math
from pymt import *
from pyglet.gl import GL_LINE_STRIP, glColor4f, glVertex2f, GL_LINE_BIT, glLineWidth

plugins = MTPlugins(plugin_paths=['..'])
plugins.search_plugins()

def gesture_add_default(gdb):
    # Circle
    g = gdb.str_to_gesture('eNqdWk2PHDcOvfcf8VwyEL8k8h5ksbcF/AMWjjPwBpt4GtNjIPn3q5LYVaxYqupsH9oYztMr1SNFvqrx06/XP39/f/7ycnv/9vZy+Yf/e02Xp1+ucPn44fb+9vrfl9uHyxUvT79d6fI0XPGxwS5XXtZJXXd9/fXr+7IsL8vKZNm/FtTlqssqq6v+rAsgXX5Kz6iskIoZgRUsmi+3jx/+WH4Ny69B2VitmBgoFYLL7edPh9cAbLdEly/9AgTCSIkZoWQtSS+3L507ZZRzunanICsdiRJgKqxYN13udD9UPjAgzEIpAyKLnpPnRl5WcpSMBVBUEnGispEDgyjkO396QIimNthKngRBLTu75I0cibjKmwtxNtJzbmx1g3DnHmTxzl31TwIJE6e6f8x2Tt4yiGsGEYgUsdIagJSEgVwze20smy/n+cSWT1zzCVjrQ9g3bhwkZymWVs3F8Jy85RPXfCYyg6pNAspJmCWQq4prsvA/UInY8omez6XeBAxJjUWK1hI32OglqaFKAW7ftcTO6KmllGClByGr6kJSZZKaxrB504J8P5elPMDeckq0si/nIwHf976UxcqeFZYD5Px10Sl7SyrJyk5QKmmCklLWhBxKhmtESxGvyfzA3ltWqWzsWVESozT+EtNaG422M9Sv8IjuLa20pZWTpZyLk5vFc4qEntHlW87PEresMjzCXo8CeAdYdp/O+xe3rPKWVa4VWVss3T+wNdsEuIpeTzM9Qt/SyvIIfT3AsWbwAWlaWjmk1VRrg/KayXljBxO4t/V6BT2vSG5Z5S2rdVLUNiONumCYQlhy2Q6qnFNLS6lsKSUsXKeFaabWC8rKXQs1b6KAnDd2aRmV83Nak8HpbzZ26a5hyydkhjqTzU/SOpKW9pg0r8WYH5j70tIp5bw9Lv2rDqvtID2QT2n5lHWYJkkA2dxTlK0H/D/kuWU0r9O0znoTqnJwG9YYNM+J12mX7Xxo5JbPfDpLl+qvaoXDz+fcLZ1ZzkzAYppqDaV13MH50c8tm7mc2a56Vcm0tfNqF8+5Wy7zZoyq6aLK6eS8cde6/5uOrrRUljWVlDPXwym1EJNJrYatYwlicC78QJ2UlsyyWdtS2YvQ3V8EK0omHLxLauTVWd8+v728fF1Ne+Hm2uXy9FMp+lxZjZ8tfuo1368lXz4tiDJHlI6QOUI7ghoi1+8asx6DFqvs8VP9zvtVU0Nkc8T3vNWtNkSeI7AjeI6gjsCGsLa3egBaDGJMeizFWNdG2g4hpf1N0ILo2ojOEV0bKXNEV0pkirCulPAc0ZUSmCO6Ujy/F+tKcQ4KWFeKKca6UgxTza3rRmWae+u6kcwRXTfCOaLrRilUXb2xFkSbFuvyfNUgegDpYmF2yPcXh9TVwn4H5FfnGIThuq4e9opNvq4Lhk1m1eGWumKIDhlRd8mwCaIyZOmagTlkwAJdQWjJUxyxQFcQmjwK/R6gawbt3osNqSlC1Nd1zaDde8nDdRIhNNxSjhB06q4ZNM1KGq7TAMnm6ywGRxVex1WEePGh69JORh5WFrpKLUe1AY0gtIcMBEEOEBkWA0qEDIsBc4Sw30MJ9yDD9KPuIaOrW4DUnjNgobSHDFgIgsjs9UIYg3lITaEYeFhSFKuOxalds3Y2eVhnlPeQEXWJEC9F0lD6a9DCOeI0IuN4GsnrkyGcYirDdRh6wQRCEeIlzN7BYBeU0J5oWNec95DR9UpojuQdk71n9fsbnge20K/HEElhFNDwyEjXjPqNed8VDEMGh31XukptvwtkRN01Iz6ASJh3E4gPzXwAKWGuTiA+NptYTdUl2BXkFIM5hTG+BrtKjLsgBmOwBt0t7C6UOdgQHDad3JUQOoDkYIgmkBJc1QSiwdBNIBa84RhSUjCYE0h0qROI29SD7RYKbngC4WCpJ5Cubjm6oxzM+j1xO4+/BjU8GozL7e7ybQ5xm69wAOkKKs2PoRt95QNIV1AlnnC3+lp2wa6S6i7YdVHbBbsudtBY3OAbzNuTO3zDOcQtvlFsju7qjXfBrkQzvJNm7E7eSmzi3cpruk+E0TrpEJjPo27tNdF8/nVvr+lginZzr0nmA7q7e015Ouaxe/07ZOQgsHv9DTJiwQ5pYkk3s9jd/T2IQ2qOEPZ1rqBOXRemHCE6pC4BkpNTawzCkNoiZDSEEVKElCEEIqRbDgQMwZKG6yhC0NdxDNJwnQQhh+4eIYc0FnHqEoqoDCsEYp35AweCxeCwbDAFiD/gIEKo6+GDESKG06FeE+i64PSZC5HDwRs+uaH7ebPp8x+6nzedPkWiu/veGfzpE93PexCG1Baajg2Lz/28yQEk9jN/Zkb3873zDZ+10f38ChlRc2ix/jIA3c/b/B0Uup+3+csMpDgDJhANs8Nfk6C7+z5l7kH38zp/HYTu7lUOIHEaTiAUZuoC2W+7QXw24gFEwvCeQHxupg7xc+9mv5R91B0F76NuIvYM7umzM9DgHt3TZzmAuPOiAwgFoziB8O5F4BAif4F8r5Q7/PvLwiGk7N4WDiH+QjEfQGz3vnAEcfcvdADxd4p4AMHda8chpKsrB+r6UwPrAcTfOe7LyR8U/hqtGvY34u+v3z7/558/Lv/xpT4NfPzw++u32wu3H+3Sfv/by9unr59fllDpf59J+w8sOH9l/+/r2+sv3z6/NzTU2fjMUBuIScLlr+hL7Pbz8/8A9Aw2sQ==')
    g.label = 'Circle'
    g.id = 'circle'
    gdb.add_gesture(g)

    # up_left, bottom_left, bottom_right, up_right
    g = gdb.str_to_gesture('eNqllt1qHEcQhe/nRaSbiPr/eQHlNqAHCI4tjIljLdo1xG+fMy1pZwRJesBiQRcz/U13nVOn+vbL6cdfl7vPj+fL9+fH5dfX/ydabj+deHm4OV+en/58PN8sJ1luv550uf3XFQ/jteVk6zrHutPTl2+XdVmsy/I/lv22vrWcal3VWPUDC5iWe7rjcDNSjzRLco3l/HDz9/qYl/tf6E5NNNRUIzKLupfzHx/+9yMs40y6fH75AnmmFVmTi3YGL+fPV3hac2hle9f6ZMYe52Z/YYNASeZJ2eySSl72M/QY9LzSuVQyvblTxVR0B1dhfFzUmBUbyDl9VJ/7SpcgIYqo6lAhlR2dwsK7M5PUXGRKl+Ek4Ssdp9ci9qD0orRd2aVDqL3SWVt9zh6Kil7ZxkYWJZImKDLFjk1NSkykanBUzP0iQ1PxI3QWLqdgZbeO9ckMPiSVPAInbqlwJm8qh2l0jh+aSu/wzekkWUkBV+YrHvQqQyt0MrFZQ5opXYemumlq0qZsWixJ1X6FC0cwtTiMg3Y70KU6NNWdpvCZd8Dl7vjMtU1Xq++feM+trkNS9QNw02TRNC9uPdSlOiTVPALPYmutKHPStgNlGYLqEUE9XKUKHhJ0aNR85zb0tE1PQWOyWrVRw5cZG7ypo6s7wnEqnTvdhqC2CYp6uhqRCPodwb7tPIhFQhHmwogCrzl8CGqboEyhbs5OTvCeblYMZitJIc7SlAPsoadteiI7sslYrNDiSCjZFA0UOlLVPaSreN6iNhS1fhtH2B57YVQYWI4w2Ngm4txOjdxC7M5r7kNQ5zc2qtqJXZWUoiq92/e7NEa6zNlDT7+OURw3U6OJMIZh6Z2cyt2Oo+CDEB15OmW/XB/8ja3vayKy+VA7KstKS53ogMl9yOl5ZaPxiBFWQoEZmrV15/vQyrmWPrT03mqiYW5laO2CKeInMiuGlrFpWeWckl0IV0GAXNn8bm6zz30SQ8vQORsZUy24JXkVHI75PIcPMcM3uGo1Jn70enlT20+4vc748LzkMeSMPEJvhkG0ROFvnIHnRowhaPQBOlIMzmyhslzTdr71HIrmpmgUkZm3YhbTGMDbfYtVMTcFGYAg5rnNc0iam6Tv7ski+3sopgM3it2yThMZ8PX3cHN5+vr4/OHbx0dcuNOGuej9H6/38dct/H56fvr0/eNlfdmX+7pDxFqs84fXARJr1t79A9YLUNw=')
    g.label = 'Square'
    g.id = 'square'
    gdb.add_gesture(g)

    # NUI-wave
    g = gdb.str_to_gesture('eNq1lttqHEcURd/7R6SXiHO//IDzGtAHBMcehIljDZoxxH+f3eXRdCskKSVBQiDBTK2urnVqn3P76fjtt/Pdw+F0/vp0WH68/D3ScvvxyMv9zen89Pjr4XSzHGW5/XzU5fYvV9yPry1HW9c51h0fP305r8tiXZZ/s+yn9VvLsdZVjVXfsIBpefcD3UmIsXqGRlJY53K6v/l9/ZzH566cxmSqUe0kupx+ef+PT2EZL6XLw+URXKwq1i7lXVpAPPx3+nh19o0u5MJRZumcSv2/6DHoeaUTNyepKouWcOaOziWSLl3uphGvoA8B3N/pgFtpp6iZaZp3x0a3xosRNl1SRh0xpcsoJuFnOmN3wu6VUZQELRvccS6R3GQW4tVz+JAq+jbw4VT8Cs/I9GC8u7CY1A4O0xmc5WRUrjKHD6WSz3ARo5RmYm5D4fgGR2lSi7alkBK7zeHDqFyNimNnEa1Nirq0XakrXc5K2ztzvnEdPpVfwRbL9hRvL+eIVxS6Dp969SlM7kBHkDcV7SqRn5+I68TwPvepw6duPtk7rEhw5oqwsR1cu1DqzpZJXjo/ch0+Nd8GPnzqdkPd2bWf76Lnrs6pG06DqTWQPO5Tug2jxrt0+VP48g4f7mIlyS6pmllz/pBqW/Jie6nZRNGs1cq7w6GX4Ug0TxgbXm2XvZHF1YVcRAmOgB140OHDJI2MEXKa4a/Y/jBr+Vb44db6ihepkM5GRqnUNcLWo/GSwOlzw2+6zuE+1PqmFp2hJQm7L8LFtdjogT6oKCwRD0O6zS+UD7G+iUVOJSNQ0HbQemR3Moxgcyorx01FWs6t+vdhYrMqHdxAX0BpGzwzuUClxnXoeYb5UOqbUvQM5hDUZDRSfjsV8ZdGc84ePn3zyQj25nZDL0VHlR0cV9WIQGVBSPA8CGL4DH4b+NAZu3uajSpnU5BCBZlzpasrGhJhColgdL15KcbwGZtP5Na+FNVyo1fCaSG8DNNH1TzDYhiNa/ySWpWiYSIMRdE86wqHzn9XLTGMxpa+mLgK9XyZs1AvGxsdryoKyUmJf+fwHEZzOh6BHSh8YShJk5ael2IOoblNR425DU0jVD00a3cmUetIhD6uyN7ucffX3/ub8+Pnw9P7Lx8OGL5x51YMvfzhdTa/7ODn49Pjx68fzuuXfXlnd4FpBhdK1kMThD7Ad38A6q5S7Q==')
    g.label = 'NUI-wave'
    g.id = 'menu'
    gdb.add_gesture(g)

    #X up_letf, bottom_right, top_right, bottom_left
    g = gdb.str_to_gesture('eNq1VttqHFcQfJ8fkV4s+n75Afk1oA8Iji2EiWMt2jXEf+86x6udSXAySoTFgmB3Tk2fqq7qvv54+PrH6ebh/nj68nS/vD3/P9By/eHAy93V8fT0+Pv98Wo5yHL96aDL9Q9P3M3HloONc45zh8ePn0/jWIxj+Q/HfhlPLYcapxqnvuIA03JLN0rRaZqhWekmthzvrv4cP/Ny+4ZuwiLYQtLFODt9Of727l9fwjLvpMvD9zeIFCBYVCOSvHM5PpzB3UzIuqqjO6RtH3xenP0ZnCusxQyvyGZqXcEts7VbKqW6m19QeUzwfAanCGJyofakSK1N6Sqpms5NTYb3v6D0yT73z0GX2UnCF3TyjHZPJg7z0uYVXkyJ8D1ol3JT2YefospZVECwUOpojm5L7ZQVnQrNBLHxQUuV0D7zMmUV/1nwU1jJFb4S93dJUZCvaWf4wZt2ZZYwwxXmQbEPP5WVvsADldukS4XImGSFTxKXMjzhqqW+T71OZZUv6MrtClEzGbZlXdG5DHqjl6IotGOfGZ266qorqE0rZwdFzlQrM+IQA1cipWQQU/vgU1VdVTXqaoVLnQilV6zgMGiUE37wthdIqlNSXSWVZBBaicZQJAnpK7CnnrrRE2dhUAaniDES+//YNtW0VU3EAJrFuxGwhUToV5BiU01b1YTLxc1RdilC1hAmr4GfetoavlQYCSg+3CtktNszdCUcrCyiaKawfQ/Z1NNyL9iH0BAD9mxDDiSPebKHPfW0S/JKob7sptJw5F9vepww4pC9LRyktp+7PvX0S+4qIBBbYERdi3LDCQliBWOuNMHVuNEe9pTT10lqsLYaI0EUTW65Gn/YPTFMkYnerPuc+PcNYtXScV2sAKRu4bmdFkRIkxFj4RjgmKgvyBWfcvo6SjtYGd1YiKhEM24GNWH/QJcmVScumLyfLD4V9XWWGjcbo3a2wj7hm1nK/3mDialpbDzKSPJA1xhsIgKCN7OUqzFBysAgyM/eh5+yxsalTcHesCL4xbKCfl3hG50+8ixHr3Ptz4uYysZmliKriwkxQGh6uQy7kfYBf2IDSeQl9sDa92lMYWOTu6gQVSO4YJcxOjcb2OAbPoA6ngYR9tGnrrFJ3sZ64hLCWE6hYW+Wx7+15b6fcuqam0lqCjsSvAT2kZXb1dRDMGURcHiDIW/20aesqZtphwmH1TMZmwbyZLPD/HCrHp+7q9Pjp/und5/f32MHh1TT3H/947Gin2v49fD0+OHL+9N42JdbHz4eaT5gDWoD9+YbKhZUkQ==')
    g.label = 'X'
    g.id = 'close'
    gdb.add_gesture(g)







def action_close_menu(menu, w, args):
    menu.parent.parent.remove_widget(menu.parent)
    del menu

def action_close_all(menu, w, args):
    sys.exit()

def action_launch_plugin(menu, w, args):
    name, plugin = args

    pos = w.parent.parent.to_parent(*w.pos)
    win = MTInnerWindow(size=(320,280), pos=pos)
    plugins.activate(plugin, win)
    menu.parent.parent.add_widget(win)

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

class MTMenuBase(MTBoxLayout):
    def __init__(self, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('uniform_width', True)
        kwargs.setdefault('uniform_height', True)
        kwargs.setdefault('color', (0,0,0,0))
        super(MTMenuBase, self).__init__(**kwargs)

        self.orig_x = self.x
        self.orig_y = self.y
        self.color = kwargs.get('color')

        plist = plugins.list()
        while len(plist):
            name, plugin = plist.popitem()
            infos = plugins.get_infos(plugin)
            w = MTActionButton(label=infos.get('title'), bgcolor=self.color,
                    action=action_launch_plugin, args=[name, plugin])
            self.add_widget(w)

        self.add_widget(MTActionButton(
            label='Close Menu', action=action_close_menu))

        self.add_widget(MTActionButton(
            label='Close PyMT', action=action_close_all))

    def on_draw(self):
        with gx_blending:
            super(MTMenuBase, self).on_draw()

    def on_move(self, x, y):
        pass

class MTMenu(MTScatterWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('pos', (0, 0))
        kwargs.setdefault('rotation', 0)
        rotation = kwargs.get('rotation')
        pos = kwargs.get('pos')
        del kwargs['rotation']
        del kwargs['pos']
        super(MTMenu, self).__init__(do_scale=False, pos=pos, rotation=rotation)
        self.menubase = MTMenuBase(**kwargs)
        self.add_widget(self.menubase)
        self.size = self.menubase.size

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
            score, best = self.gdb.find(gesture, minscore=.7)
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
