'''
Box layout: arrange widget in horizontal or vertical
'''

__all__ = ['MTBoxLayout']

from abstractlayout import MTAbstractLayout
from ...factory import MTWidgetFactory

class MTBoxLayout(MTAbstractLayout):
    '''Box layout can arrange item in horizontal or vertical orientation.
    :Parameters:
        `padding` : int, default to 0
            Padding between the border and content
        `spacing` : int, default to 1
            Spacing between widgets
        `orientation` : str, default is 'horizontal'
            Orientation of widget inside layout, can be `horizontal` or `vertical`
        'invert': bool, default to False
            makes the layout do top to bottom on horizontal, or rigth to left on vertical
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('spacing', 1)
        kwargs.setdefault('padding', 0)
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('invert', False)
        if kwargs.get('orientation') not in ['horizontal', 'vertical']:
            raise Exception('Invalid orientation, only horizontal/vertical are supported')

        super(MTBoxLayout, self).__init__(**kwargs)

        self.spacing      = kwargs.get('spacing')
        self.padding      = kwargs.get('padding')
        self._orientation = kwargs.get('orientation')
        self._invert      =  kwargs.get('invert')

    def add_widget(self, widget, front=False, do_layout=None):
        if self._invert:
            front = not front
        super(MTBoxLayout, self).add_widget(widget, front, do_layout)

    def _get_orientation(self):
        return self._orientation
    def _set_orientation(self, orientation):
        if self._orientation == orientation:
            return
        elif orientation in ['horizontal', 'vertical']:
            self._orientation = orientation
            self.do_layout()
        else:
            raise ValueError("'%s' is not a valid orientation for BoxLayout!  Allowed values are: 'horizontal' and 'vertical'." % orientation)
    orientation = property(_get_orientation, _set_orientation, doc="Orientation of widget inside layout, can be `horizontal` or `vertical`")

    def do_layout(self):
        width  = self.padding*2
        height = self.padding*2

        if self.orientation == 'horizontal':
            total_width = 0
            hint_width = 0
            for w in reversed(self.children):
                if w.size_hint[0]:
                    hint_width += w.size_hint[0]
                else:
                    total_width += w.width
                total_width += self.spacing
            room_left = max(0,self.width - total_width)
            x = self.x + self.padding
            y = self.y + self.padding
            for c in reversed(self.children):
                w,h = c.size
                if c.size_hint[0]:
                    w = room_left*c.size_hint[0]/max(1.0, float(hint_width))
                if c.size_hint[1]:
                    h = max(1.0, c.size_hint[1])*self.height
                self.reposition_child(c, pos=(x,y), size=(w,h))
                x += w+self.spacing
                width += w+self.spacing
                height = max(height, h+self.padding*2)

        if self.orientation == 'vertical':
            total_height = 0
            hint_height = 0
            for w in self.children:
                if w.size_hint[1]:
                    hint_height += w.size_hint[1]
                else:
                    total_height += w.height
                total_height += self.spacing
            room_left = max(0,self.height - total_height)
            x = self.x + self.padding
            y = self.y + self.padding
            for c in self.children:
                w,h = c.size
                if c.size_hint[0]:
                    w = max(1.0, c.size_hint[0])*self.width
                if c.size_hint[1]:
                    h = room_left*c.size_hint[1]/max(1.0, float(hint_height))
                self.reposition_child(c, pos=(x,y), size=(w,h))
                y += h+self.spacing
                height += h+self.spacing
                width = max(width, w+self.padding*2)

        self.width  = max(width+self.padding, self.width)
        self.height = max(height+self.padding, self.height)

        self.dispatch_event('on_layout')


# Register all base widgets
MTWidgetFactory.register('MTBoxLayout', MTBoxLayout)
