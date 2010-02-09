import random
from pymt import *




class TestWidget(MTWidget):
    _id = 0
    def __init__(self, **kwargs):
        super(TestWidget, self).__init__(**kwargs)
        TestWidget._id += 1
        self.label = str(TestWidget._id)
        self.color = map(lambda x: random.random(), xrange(3))
        self.size = map(lambda x: random.randint(50, 100), xrange(2))
    def draw(self):
        set_color(*self.color)
        drawRectangle(pos=self.pos, size=self.size)
        drawLabel(pos=self.pos, center=False, label=self.label)

if __name__ == '__main__':

    # create a layout with 20 children
    grid = MTBoxLayout(animation_type='ease_in_out_cubic')
    for i in xrange(20):
        grid.add_widget(TestWidget())

    # Every second, bring the first children to front
    def bring(*largs):
        first = grid.children.pop()
        grid.add_widget(first, front=False)
    getClock().schedule_interval(bring, 1)

    # Run !
    runTouchApp(grid)

