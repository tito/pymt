from pymt.ui.widgets.widget import MTWidget

class MTAbstractFormWidget(MTWidget):
    '''Abstract form widget. Base class used to implement any form widget.
    '''

    def __init__(self, **kwargs):
        if self.__class__ == MTAbstractFormWidget:
            raise NotImplementedError, 'class MTAbstractFormWidget is abstract'
        super(MTAbstractFormWidget, self).__init__(**kwargs)

    def on_resize(self, w, h):
        layout = self.get_parent_layout()
        if layout:
            layout.do_layout()
        super(MTAbstractFormWidget, self).on_resize(w, h)

