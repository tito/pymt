from pymt.ui.widget import MTWidget

"""TODO: Layouts...not used anywhere yet"""
class HorizontalLayout(MTWidget):
    def __init__(self, spacing=10, **kargs):
        MTWidget.__init__(self, **kargs)
        self.spacing = spacing

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

