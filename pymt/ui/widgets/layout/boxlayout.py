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
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('spacing', 1)
        kwargs.setdefault('padding', 0)
        kwargs.setdefault('orientation', 'horizontal')
        if kwargs.get('orientation') not in ['horizontal', 'vertical']:
            raise Exception('Invalid orientation, only horizontal/vertical are supported')

        super(MTBoxLayout, self).__init__(**kwargs)

        self.spacing        = kwargs.get('spacing')
        self.padding        = kwargs.get('padding')
        self._orientation    = kwargs.get('orientation')
        
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
     
        if self.orientation == 'horizontal':
            total_width = 0
            hint_width = 0
            for w in self.children:
                if w.size_hint[0]:
                    hint_width += w.size_hint[0]
                else:
                    total_width += w.width
            room_left = max(0,self.width - total_width)
            x = self.x + self.padding
            y = self.y + self.padding
            for c in self.children:
                w,h = c.size
                if c.size_hint[0]:
                    w = room_left*c.size_hint[0]/min(1.0, float(hint_width))
                w +=  self.spacing
                if c.size_hint[1]:
                    h = max(1.0, c.size_hint[1])*self.height                
                self.reposition_child(c, pos=(x,y), size=(w,h))

        if self.orientation == 'vertical':
            total_height = 0
            hint_height = 0
            for w in self.children:
                if w.size_hint[1]:
                    hint_height += w.size_hint[1]
                else:
                    total_height += w.height
            room_left = max(0,self.height - total_height)
            x = self.x + self.padding
            y = self.y + self.padding
            for c in self.children:
                w,h = c.size
                if c.size_hint[0]:
                    w = min(1.0, c.size_hint[0]*self.width)
                if c.size_hint[1]:
                    h = room_left*c.size_hint[1]/min(1.0, float(hint_height))
                h +=  self.spacing
                self.reposition_child(c, pos=(x,y), size=(w,h))

        # we just do a layout, dispatch event
        self.dispatch_event('on_layout')

# Register all base widgets
MTWidgetFactory.register('MTBoxLayout', MTBoxLayout)
