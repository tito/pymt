# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'FlowChart'
PLUGIN_AUTHOR = 'Mathieu Virbel'
PLUGIN_DESCRIPTION = 'A test for doing some flowchart'

from pymt import *
from OpenGL.GL import GL_LINE_LOOP

flowcss = '''
flowchart {
    bg-color: rgba(255, 255, 255, 255);
}
flowtext {
    draw-background: 0;
    draw-border: 0;
    color: rgb(255, 255, 255);
}
'''
css_add_sheet(flowcss)


class FlowText(MTTextInput):
    def __init__(self, **kwargs):
        kwargs.setdefault('padding_x', 10)
        kwargs.setdefault('autosize', True)
        super(FlowText, self).__init__(**kwargs)
        self.orig = (0, 0)
        self.label_obj.options['font_size'] = self.height / 2.
        self.label_obj.refresh()

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
        self.add_widget(self.label)

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
        self.width = max(100, self.label.width)
        set_color(.435, .749, .996)
        drawRoundedRectangle(size=self.size)
        set_color(.094, .572, .858)
        drawRoundedRectangle(size=self.size, linewidth=2, style=GL_LINE_LOOP)
        # 24 146 219 (black)
        # 111 191 254 (white)


class FlowLink(MTWidget):
    def __init__(self, **kwargs):
        super(FlowLink, self).__init__(**kwargs)
        self.node1 = kwargs.get('node1')
        self.node2 = kwargs.get('node2')

    def draw(self):
        if isinstance(self.node2, FlowElement):
            node2p = self.node2.center
        else:
            node2p = self.node2.pos
        ax, ay = self.to_widget(*self.to_window(*self.node1.center))
        if type(self.node2) == FlowElement:
            bx, by = self.to_widget(*self.to_window(*node2p))
        else: # touch case
            bx, by = self.parent.to_local(*node2p)
        set_color(.094, .572, .858)
        drawLine((ax, ay, bx, by), width=8. * self.parent.scale)


class FlowChart(MTScatterPlane):
    def __init__(self, **kwargs):
        kwargs.setdefault('do_rotation', False)
        kwargs.setdefault('scale_min', 0.2)
        kwargs.setdefault('scale_max', 1.0)
        super(FlowChart, self).__init__(**kwargs)
        self.keyboard = MTVKeyboard()
        self.show_ui_help = True
        self.inactivity_timer = 0

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
        self.show_ui_help = False
        self.inactivity_timer = 0
        if touch.is_double_tap:
            node = self.find_node(x, y)
            if node:
                touch.grab(self)
                link = self.create_link(node, touch)
                self.disable_all()
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
            if node is None or node == link.node1:
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
            color=(0, 0, 0, 50))
        drawLabel(label='+', pos=(w.width - 25, 250), font_size=40,
            color=(0, 0, 0, 50))
        set_color(0, 0, 0, .1)
        drawRoundedRectangle(pos=(w.width - 40, 40), size=(30, 175))
        set_color(0, 0, 0, .1)
        drawRoundedRectangle(pos=(w.width - 40, 40),
             size=(30, 175 * self.scale))

        self.inactivity_timer += getFrameDt()
        if self.inactivity_timer > 10:
            self.show_ui_help = True
        if self.show_ui_help:
            p = w.width / 2., 50
            c = (0, 0, 0, 180)
            fs = 22
            set_color(0, 0, 0, .1)
            w2 = (w.width - 750) / 2.
            drawRoundedRectangle(pos=(w2, 20), size=(w.width - w2 * 2, 140))
            drawLabel(label='Double-tap on background to create a node',
                      pos=p, color=c, font_size=24)
            p = w.width / 2., 90
            drawLabel(label='Double-tap & hold on a node to create a link',
                      pos=p, color=c, font_size=24)
            p = w.width / 2., 130
            drawLabel(label='Tap a node to toggle keyboard',
                      pos=p, color=c, font_size=24)

    def on_draw(self):
        w = self.get_parent_window()
        set_color(*self.style['bg-color'])
        drawRectangle(size=w.size)
        super(FlowChart, self).on_draw()
        self.draw_ui()

    def draw(self):
        w = self.get_parent_window()
        a = self.to_local(0, 0)
        b = self.to_local(w.width, w.height)
        scale = max(1, int(1 / self.scale))
        step = 200 * scale
        a = int(a[0] / step - 1) * step, int(a[1] / step - 1) * step
        b = int(b[0] / step + 1) * step, int(b[1] / step + 1) * step
        for x in xrange(a[0], b[0], step):
            for y in xrange(a[1], b[1], step):
                set_color(.9, .9, .9)
                drawLine((a[0], y, b[0], y), width=1)
                drawLine((x, a[1], x, b[1]), width=1)

def pymt_plugin_activate(root, ctx):
    ctx.flowchart = FlowChart()
    root.add_widget(ctx.flowchart)

def pymt_plugin_deactivate(root, ctx):
    root.remove_widget(ctx.flowchart)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
