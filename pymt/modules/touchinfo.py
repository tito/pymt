'''
Get all informations of a touch
'''

from pymt import MTWidget, MTSpeechBubble

class TouchInfos(MTWidget):
    def __init__(self, **kwargs):
        super(TouchInfos, self).__init__(**kwargs)
        self.bubbles = {}

    def text_info(self, touch):
        infos = []
        infos.append('ID: %s' % (str(touch.blobID)))
        infos.append('Raw pos: (%f, %f)' % (touch.sx, touch.sy))
        infos.append('Scr Pos: (%d, %d)' % (touch.xpos, touch.ypos))
        if hasattr(touch, 'xmot'):
            infos.append('Mot: (%.2f, %.2f)' % (touch.xmot, touch.ymot))
        infos.append('Double Tap: %s' % (touch.is_double_tap))
        infos.append('Device: %s' % (touch.device))
        return "\n".join(infos)

    def on_touch_down(self, touch):
        self.bubbles[touch.id] = MTSpeechBubble(pos=(touch.x, touch.y),
                                                size=(200, 100),
                                                color=(0, 0, 0, 1))
        self.bubbles[touch.id].label = self.text_info(touch)

    def on_touch_move(self, touch):
        if not touch.id in self.bubbles:
            return
        self.bubbles[touch.id].pos = (touch.x, touch.y)
        self.bubbles[touch.id].label = self.text_info(touch)

    def on_touch_up(self, touch):
        if touch.id in self.bubbles:
            del self.bubbles[touch.id]

    def on_update(self):
        self.bring_to_front()

    def draw(self):
        for bubble in self.bubbles:
            self.bubbles[bubble].dispatch_event('on_draw')

def start(win, ctx):
    ctx.w = TouchInfos()
    win.add_widget(ctx.w)

def stop(win, ctx):
    win.remove_widget(ctx.w)
