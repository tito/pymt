'''
Container: easy way to convert a simple BaseObject into a widget
'''

__all__ = ('MTContainer', 'MTScatterContainer')

from pymt.logger import pymt_logger
from pymt.ui.widgets.widget import MTWidget
from pymt.ui.widgets.scatter import MTScatterWidget

class MTContainer(MTWidget):
    '''Convert a BaseObject like into a MTWidget.

    :Parameters:
        `fit_to_parent` : bool, default to True
            set baseobject size to parent size
    '''
    def __init__(self, baseobject, **kwargs):
        kwargs.setdefault('fit_to_parent', True)
        super(MTContainer, self).__init__(**kwargs)
        self.fit_to_parent = kwargs.get('fit_to_parent')
        self.child = baseobject
        self.size = self.child.size

    def add_widget(self, widget):
        pymt_logger.warning('MTContainer: cannot add MTWidget, only take BaseObject')

    def on_parent_resize(self, w, h):
        if self.fit_to_parent:
            self.size = w, h

    def on_resize(self, w, h):
        # if our size have changed, update children
        self.child.size = w, h

    def on_update(self):
        super(MTContainer, self).on_update()
        self.child.update()

    def draw(self):
        super(MTContainer, self).draw()
        self.child.pos = self.pos
        self.child.draw()

class MTScatterContainer(MTContainer, MTScatterWidget):
    '''Convert a BaseObject like into a MTScatterWidget.'''
    def draw(self):
        # just subclass this function, don't move the object :)
        super(MTContainer, self).draw()
        self.child.draw()

