from pymt.ui.widget import MTWidget
from pymt.ui.ui import MTRectangularWidget

"""TODO: Layouts...not used anywhere yet"""
class HorizontalLayout(MTRectangularWidget):
    def __init__(self, parent=None, spacing=10, **kargs):
        MTRectangularWidget.__init__(self, parent, **kargs)
        self.spacing = spacing

    def draw(self):
        MTWidget.draw(self)

    def add_widget(self,w):
        MTWidget.add_widget(self, w)
        self.layout()

    def layout(self):
        cur_x = self.x
        for w in self.children:
            try:
                w.x = cur_x
                cur_x += w.width + spacing
            except:
                pass





