from pymt.ui.widget import MTWidget

"""TODO: Layouts...not used anywhere yet"""
class HorizontalLayout(MTWidget):
    def __init__(self, spacing=10, **kargs):
        super(HorizontalLayout, self).__init__(**kargs)
        self.spacing = spacing

    def add_widget(self, w):
        super(HorizontalLayout, self).add_widget(w)
        self.layout()

    def layout(self):
        cur_x = self.x
        for w in self.children:
            try:
                w.x = cur_x
                cur_x += w.width + spacing
            except:
                pass

