'''
Abstract form widget: base for every form widget
'''

__all__ = ['MTAbstractFormWidget']

from ..widget import MTWidget

class MTAbstractFormWidget(MTWidget):
    '''Abstract form widget. Base class used to implement any form widget.
    '''

    def __init__(self, **kwargs):
        if self.__class__ == MTAbstractFormWidget:
            raise NotImplementedError, 'class MTAbstractFormWidget is abstract'
        super(MTAbstractFormWidget, self).__init__(**kwargs)

    def _remove_widget(self, widget):
        super(MTAbstractFormWidget, self).remove_widget(widget)

    def _add_widget(self, widget):
        super(MTAbstractFormWidget, self).add_widget(widget)

    def add_widget(self, widget):
        raise Exception('Cannot add widget into form widget')

    def remove_widget(self, widget):
        raise Exception('Cannot remove widget from a form widget')

    def on_resize(self, w, h):
        layout = self.get_parent_layout()
        if layout:
            layout.do_layout()
        super(MTAbstractFormWidget, self).on_resize(w, h)

