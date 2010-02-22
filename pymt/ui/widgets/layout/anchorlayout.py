'''
Anchor layout: Anchors its child widgtes to a certain section of the parent, like left, top, center, rigth etc
'''

__all__ = ['MTAnchorLayout']

from abstractlayout import MTAbstractLayout
from ...factory import MTWidgetFactory
from ....base import getWindow

class MTAnchorLayout(MTAbstractLayout):
    '''MTAnchorLayout layout: anchorts the Child Widgets to a certain place in the parent widget.
        AnchorLayout does not resize children (it ignores size_hint), us a box layout, or other layout inside anchor layout instead)

    :Parameters:
        `padding` : int, default to 0
            Padding between the border and children (ignored if anchor is center!)
        `anchor_x` : str, default to 'center'
            Horizontal Anchor.  One of: 'left', 'right, or bottom', 'center'.  default is center "
        `anchor_y` : str, default to 'center'
            Vertical Anchor.  One of: 'top', 'bottom', or 'center'.  default is center "
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('padding',  0)
        kwargs.setdefault('anchor_x','center')
        kwargs.setdefault('anchor_y', 'center')
        super(MTAnchorLayout, self).__init__(**kwargs)
        
        self.padding  = kwargs.get('padding')
        self.anchor_x = kwargs.get('anchor_x')
        self.anchor_y = kwargs.get('anchor_y')
        
        
        
    def _get_anchor_x(self):
        return self._anchor_x
    def _set_anchor_x(self, anchor):
        if anchor in ['left', 'right', 'center']:
            self._anchor_x = anchor
            self.need_layout = True
            self.do_layout()
        else:
            raise ValueError("'%s' is not a valid anchor for horizontal(X) axis!  Allowed values are: 'center', 'left', or 'right'." % anchor)
    anchor_x = property(_get_anchor_x, _set_anchor_x, doc="Horizontal Anchor.  One of: 'left', 'right, or 'center'.  default is center ")

    def _get_anchor_y(self):
        return self._anchor_y
    def _set_anchor_y(self, anchor):
        if anchor in ['top', 'bottom', 'center']:
            self._anchor_y = anchor
            self.need_layout = True
            self.do_layout()
        else:
            raise ValueError("'%s' is not a valid anchor for vertical(Y) axis!  Allowed values are: 'center', 'top', or 'bottom'." % anchor)
    anchor_y = property(_get_anchor_y, _set_anchor_y, doc="Vertical Anchor.  One of: 'top', 'bottom, or 'center'.  default is center ")
   
   
    def do_layout(self):
        super(MTAnchorLayout, self).do_layout()
        for w in self.children:
            x,y = self.pos 
            
            if self.anchor_x == 'left':
                x = self.x + self.padding
            if self.anchor_x == 'right':
                x = self.x + self.width - (w.width+self.padding)
            if self.anchor_x == 'center':
                x = self.x + (self.width/2) - (w.width/2)
                
            if self.anchor_y == 'bottom':
                y = self.y + self.padding
            if self.anchor_y == 'top':
                y = self.y + self.height - (w.height+self.padding)
            if self.anchor_y == 'center':
                y = self.y + (self.height/2) - (w.height/2)
            
            self.reposition_child(w, pos=(x,y))

        self.dispatch_event('on_layout')


# Register all base widgets
MTWidgetFactory.register('MTAnchorLayout', MTAnchorLayout)
