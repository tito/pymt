from pymt import *
from pyglet.gl import GL_LINE_LOOP


class FlowText(MTTextInput):
    def __init__(self, **kwargs):
        super(FlowText, self).__init__(**kwargs)
        self.orig = (0, 0)

    def on_press(self, touch):
        self.orig = Vector(self.to_window(*touch.pos))

    def on_release(self, touch):
        final = Vector(self.to_window(*touch.pos))
        if self.orig.distance(final) <= 4:
            if not self.is_active_input:
                self.parent.disable_all()
            super(FlowText, self).on_press(touch)

    def on_touch_down(self, touch):
        super(FlowText, self).on_touch_down(touch)
        return False


class FlowElement(MTScatterWidget):
    def __init__(self, **kwargs):
        super(FlowElement, self).__init__(**kwargs)
        self.editmode = True
        self.label = FlowText(style={'font-size': self.height / 2.},
                              keyboard=kwargs.get('keyboard'))
        self.label.push_handlers(on_text_change=self._on_text_change)
        self.add_widget(self.label)

    def _on_text_change(self, text):
        self.width = max(100, self.label.width)

    def disable_all(self):
        self.parent.disable_all()

    def disable(self):
        self.label.hide_keyboard()

    def enable(self):
        self.label.show_keyboard()

    def draw(self):
        '''
        set_color(.509, .407, .403, .95)
        drawRoundedRectangle(size=self.size)
        set_color(.298, .184, .192, .95)
        drawRoundedRectangle(size=self.size, linewidth=2, style=GL_LINE_LOOP)
        '''

        set_color(.435, .749, .996, .95)
        drawRoundedRectangle(size=self.size)
        set_color(.094, .572, .858, .95)
        drawRoundedRectangle(size=self.size, linewidth=2, style=GL_LINE_LOOP)
        # 24 146 219 (black)
        # 111 191 254 (white)


class FlowLink(MTWidget):
    def __init__(self, **kwargs):
        super(FlowLink, self).__init__(**kwargs)
        self.node1 = kwargs.get('node1')
        self.node2 = kwargs.get('node2')

    def draw(self):
        ax, ay = self.to_widget(*self.to_window(*self.node1.pos))
        bx, by = self.to_widget(*self.to_window(*self.node2.pos))
        set_color(1, 1, 1)
        drawLine((ax, ay, bx, by), width=8. * self.parent.get_scale_factor())


class FlowChart(MTScatterPlane):
    def __init__(self, **kwargs):
        kwargs.setdefault('do_rotation', False)
        kwargs.setdefault('scale_min', 0.2)
        kwargs.setdefault('scale_max', 1.0)
        super(FlowChart, self).__init__(**kwargs)
        self.keyboard = MTVKeyboard()

    def create_node(self, x, y):
        node = FlowElement(pos=(x, y), keyboard=self.keyboard)
        self.add_widget(node, front=True)
        return node

    def create_link(self, node1, node2):
        link = FlowLink(node1=node1, node2=node2)
        self.add_widget(link, front=False)
        return link

    def find_node(self, x, y):
        for c in self.children:
            if c.collide_point(x, y):
                return c

    def on_touch_down(self, touch):
        x, y = self.to_local(*touch.pos)
        if touch.is_double_tap:
            node = self.find_node(x, y)
            if node:
                touch.grab(self)
                link = self.create_link(node, touch)
                touch.userdata['flow.link'] = link
            else:
                node = self.create_node(x - 50, y - 50)
                self.disable_all()
                node.enable()
            return True
        return super(FlowChart, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        x, y = self.to_local(*touch.pos)
        if touch.grab_current == self and 'flow.link' in touch.userdata:
            link = touch.userdata['flow.link']
            node = self.find_node(x, y)
            if node is None:
                self.remove_widget(link)
            else:
                link.node2 = node
        return super(FlowChart, self).on_touch_up(touch)


    def disable_all(self):
        for w in self.children:
            if type(w) != FlowElement:
                continue
            w.disable()

    def draw_ui(self):
        w = self.get_parent_window()
        drawLabel(label='-', pos=(w.width - 25, 25), font_size=40,
            color=(255, 255, 255, 50))
        drawLabel(label='+', pos=(w.width - 25, 250), font_size=40,
            color=(255, 255, 255, 50))
        set_color(1, 1, 1, .1)
        drawRoundedRectangle(pos=(w.width - 40, 40), size=(30, 175))
        set_color(1, 1, 1, .1)
        drawRoundedRectangle(pos=(w.width - 40, 40),
             size=(30, 175 * self.get_scale_factor()))

    def on_draw(self):
        super(FlowChart, self).on_draw()
        self.draw_ui()


if __name__ == '__main__':
    m = MTWindow()
    m.add_widget(FlowChart())
    runTouchApp()
