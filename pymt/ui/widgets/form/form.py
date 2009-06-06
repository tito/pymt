'''
Form: a form container
'''
__all__ = ['MTForm']

from abstract import MTAbstractFormWidget
from ....graphx import set_color, drawRoundedRectangle, drawRectangle
from ...factory import MTWidgetFactory

class MTForm(MTAbstractFormWidget):
    '''Form container : with a basic layout, you can add form widget in it,
    and create simple container with basic event (cancel, submit...)

    :Parameters:
        `layout` : MTAbstractLayout class, default is None
            Initial layout to be used with form

    :Styles:
        `border-radius` : int, default to 0
            Border radius of background
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('layout', None)
        super(MTForm, self).__init__(**kwargs)
        self.layout = kwargs.get('layout')

    def _set_layout(self, layout):
        if hasattr(self, '_layout') and self._layout:
            super(MTForm, self)._remove_widget(self._layout)
        self._layout = layout
        if self._layout:
            super(MTForm, self)._add_widget(self._layout)
    def _get_layout(self):
        return self._layout
    layout = property(_get_layout, _set_layout)

    def add_widget(self, widget):
        self.layout.add_widget(widget)

    def draw(self):
        set_color(*self.style.get('bg-color'))
        if int(self.style.get('border-radius')) > 0:
            drawRoundedRectangle(pos=self.pos, size=self.size, radius=int(self.style.get('border-radius')))
        else:
            drawRectangle(pos=self.pos, size=self.size)

    def get_parent_layout(self):
        return self

    def do_layout(self):
        self.size = self.layout.content_width, self.layout.content_height

    def on_move(self, x, y):
        super(MTForm, self).on_move(x, y)
        self.layout.pos = self.pos
        self.layout.do_layout()


# Register all base widgets
MTWidgetFactory.register('MTForm', MTForm)
