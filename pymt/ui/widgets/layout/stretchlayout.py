'''
Stretch layout: stretches the Child Widgets to fit exactly inside the target (parent by default)
'''

__all__ = ['MTStretchLayout']

from abstractlayout import MTAbstractLayout
from ...factory import MTWidgetFactory
from ....base import getWindow

class MTStretchLayout(MTAbstractLayout):
    '''Stretch layout: stretches the Child Widgets to fit exactly inside the parent

    :Parameters:
        `padding` : int, default to 0
            Padding between the border and children (that much smaller than the parent on each side)
            
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('padding', 0)
        super(MTStretchLayout, self).__init__(**kwargs)
        
        self.padding  = kwargs.get('padding')

        self.push_handlers(on_parent_resize=self.require_layout)
        self.push_handlers(on_parent=self.require_layout)

               
    def stretch_to_parent(self):
        '''Sets own size and pos to that of parent (minus padding).
           Uses Window size and (0,0) for pos if no parent is set.
        '''
        #get position and size of parent (maybe window...then no pos, so use (0,0))
        if not self.parent: #if no parent..stretch to window size
            self.parent = getWindow()
        
        if  self.parent == getWindow():
            self.pos = (0,0)
        else:
            self.pos = self.parent.pos
        self.size = self.parent.size

    def do_layout(self):
        '''Set own size and pos and that of child widgets to that of parent (minus padding).
           Dispatches on_layout event when done.
        '''
        super(MTStretchLayout, self).do_layout()

        self.stretch_to_parent()                   
        for w in self.children:
            pos  = (self.x+self.padding, self.y-self.padding)
            size = (self.width-(2*self.padding), self.height-(2*self.padding))
            self.reposition_child(w, pos=pos, size=size)
        # we just do a layout, dispatch event
        self.dispatch_event('on_layout')

# Register all base widgets
MTWidgetFactory.register('MTStretchLayout', MTStretchLayout)
