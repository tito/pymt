'''
Anchor layout: Align child widget to a border or center.

Anchors its child widgtes to a certain section of the parent,
like left, top, center, rigth...
'''

__all__ = ('MTAnchorLayout', )

from pymt.ui.widgets.layout.abstractlayout import MTAbstractLayout

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

        super(MTAnchorLayout, self).__init__(**kwargs)

        self._anchor_x = kwargs.get('anchor_x', 'center')
        self._anchor_y = kwargs.get('anchor_y', 'center')
        self.padding  = kwargs.get('padding')


    def _get_anchor_x(self):
        return self._anchor_x
    def _set_anchor_x(self, anchor):
        if anchor in ['left', 'right', 'center']:
            self._anchor_x = anchor
            self.need_layout = True
            self.do_layout()
        else:
            raise ValueError("'%s' is not a valid anchor for horizontal(X) axis!  Allowed values are: 'center', 'left', or 'right'." % anchor)
    anchor_x = property(_get_anchor_x, _set_anchor_x,
                        doc="Horizontal Anchor.  One of: 'left', 'right', or" +
                            "'center'.  default is center ")

    def _get_anchor_y(self):
        return self._anchor_y
    def _set_anchor_y(self, anchor):
        if anchor in ['top', 'bottom', 'center']:
            self._anchor_y = anchor
            self.need_layout = True
            self.do_layout()
        else:
            raise ValueError("'%s' is not a valid anchor for vertical(Y) axis!  Allowed values are: 'center', 'top', or 'bottom'." % anchor)
    anchor_y = property(_get_anchor_y, _set_anchor_y,
                        doc="Vertical Anchor.  One of: 'top', 'bottom', or" +
                            "'center'.  default is center ")


    def do_layout(self):
        # only acces properties once, instead of every time inside loop for
        # optimization.
        _x, _y = self.pos
        width, height = self.size
        anchor_x, anchor_y = self.anchor_x, self.anchor_y
        padding = self.padding
        reposition_child = self.reposition_child

        for c in self.children:
            x, y = _x, _y
            w, h = c.size
            if c.size_hint[0]:
                w = c.size_hint[0]*width
            elif not self.size_hint[0]:
                width = max(width, c.width)
            if c.size_hint[1]:
                h = c.size_hint[1]*height
            elif not self.size_hint[1]:
                height = max(height, c.height)

            if anchor_x == 'left':
                x = x + padding
            if anchor_x == 'right':
                x = x + width - (w + padding)
            if self.anchor_x == 'center':
                x = x + (width / 2) - (w / 2)
            if anchor_y == 'bottom':
                y = y + padding
            if anchor_y == 'top':
                y = y + height - (h + padding)
            if anchor_y == 'center':
                y = y + (height / 2) - (h / 2)

            reposition_child(c, pos=(x, y), size=(w, h))

        self.size = (width, height) #might have changed inside loop
        self.dispatch_event('on_layout')
