from pymt import *
from random import randint

class objectWindow(MTWindow):
    def __init__(self, **kwargs):
        super(objectWindow, self).__init__(**kwargs)
        self.objects = {}
        self.colors = {}

    def draw(self):
        super(objectWindow, self).draw()
        for id in self.objects:
            obj = self.objects[id]
            if not obj.id in self.colors:
                self.colors[obj.id] = (
                    randint(0, 255) / 255.0,
                    randint(0, 255) / 255.0,
                    randint(0, 255) / 255.0
                )
            set_color(*self.colors[obj.id])
            drawCircle(pos=(obj.xpos * self.width, (1 - obj.ypos) * self.height),
                            radius=(obj.angle * 10))

    def on_object_down(self, objects, objectID, id, x, y, angle):
        self.objects = objects

    def on_object_move(self, objects, objectID, id, x, y, angle):
        self.objects = objects

    def on_object_up(self, objects, objectID, id, x, y, angle):
        self.objects = objects

win = objectWindow(fullscreen=False, size=(1024,768))
runTouchApp()

