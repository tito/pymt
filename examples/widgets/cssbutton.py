from pymt import *

additional_css = '''
.simple {
	draw-alpha-background: 1;
	draw-border: 1;
	draw-slider-alpha-background: 1;
	draw-slider-border: 1;
	draw-text-shadow: 1;
}

.colored {
	bg-color: #ff5c00;
	border-radius: 20;
	border-radius-precision: .1;
	font-size: 16;
	slider-border-radius-precision: .1;
	slider-border-radius: 20;
}

boundaryslider.colored,
xyslider.colored,
slider.colored {
	bg-color: #222222;
}
'''

class ObjectPicker(MTWidget):
    def __init__(self, **kwargs):
        super(ObjectPicker, self).__init__(**kwargs)
        self.touchid = None
        self.touchpos = (0, 0)
        self.size = (25, 25)
    def pick(self, x, y):
        w = self.get_parent_window()
        if not w:
            return
        return self.subpick(w, x, y)
    def subpick(self, wid, x, y):
        if hasattr(wid, 'collide_point'):
            if not wid.collide_point(x, y):
                return None
        if not hasattr(wid, 'children'):
            return wid
        for w in wid.children:
            r = self.subpick(w, x, y)
            if r:
                return r
        return wid
    def on_touch_down(self, touches, touchID, x, y):
        if not self.collide_point(x, y):
            return
        self.touchid = touchID
        self.touchpos = (x, y)
        return True
    def on_touch_move(self, touches, touchID, x, y):
        if self.touchid == touchID:
            self.touchpos = (x, y)
            return True
    def on_touch_up(self, touches, touchID, x, y):
        if self.touchid == touchID:
            self.touchid = None
            self.touchpos = (0, 0)
            return True
    def get_infos(self, wid):
        x = []
        x.append('Class: %s' % str(wid.__class__).split('.')[-1][:-2])
        if hasattr(wid, 'pos'):
            x.append('Pos: %s)' % str(wid.pos))
        x.append('Size: %s' % str(wid.size))
        if hasattr(wid, 'cls') and wid.cls:
            x.append('CSS: %s' % str(wid.cls))
        return "\n".join(x)

    def draw(self):
        if self.touchid:
            set_color(1, 1, 1, .25)
        else:
            set_color(*self.style['bg-color'])
        drawCSSRectangle(pos=self.pos, size=self.size, style=self.style)
        if self.touchid:
            r = self.pick(*self.touchpos)
            drawLabel(label=self.get_infos(r), center=False, pos=self.pos, width=200, multiline=True, font_size=10)

            set_color(1, 0, 0, .25)
            rpos = (0, 0)
            if hasattr(r, 'pos'):
                rpos = r.pos
            drawRectangle(pos=rpos, size=r.size)

css_add_sheet(additional_css)

m = MTWindow()

h = MTBoxLayout(pos=(200, 0), padding=20, spacing=20)

v = MTBoxLayout(orientation='vertical', padding=20, spacing=20)
v.add_widget(MTButton(label='Coucou'))
v.add_widget(MTButton(label='Coucou', cls='simple'))
v.add_widget(MTButton(label='Coucou', cls=('simple', 'colored')))
h.add_widget(v)
v2 = MTBoxLayout(orientation='vertical', padding=20, spacing=20)
v2.add_widget(MTSlider(orientation='horizontal', value=50))
v2.add_widget(MTSlider(cls=('simple', 'colored'), orientation='horizontal', value=50))
v2.add_widget(MTBoundarySlider(orientation='horizontal', value=50))
v2.add_widget(MTBoundarySlider(cls=('simple', 'colored'), orientation='horizontal', value=50))
v2.add_widget(MTXYSlider(cls=('simple', 'colored')))
h.add_widget(v2)

m.add_widget(h)
#m.add_widget(ObjectPicker())
runTouchApp()
