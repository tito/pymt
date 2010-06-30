'''
Box layout: arrange widget in horizontal or vertical
'''

__all__ = ('MTBoxLayout', )

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


    def update_minimum_size(self):
        '''
        calculates the minimum size of teh layout
        there mus be room for child widgets that have fixed size (size_hint == None)
        there must also be at least enough room for every child layout's minimum size (cant be too small even if size_hint is set)
        '''
        padding = self.padding
        spacing = self.spacing
        width  = padding
        height = padding

        if self.orientation == 'horizontal':
            width += (len(self.children) -1) * spacing
            for w in self.children:
                if w.size_hint[0] == None:
                    width += w.width + padding
                if w.size_hint[1] == None:
                    height = max(w.height + padding, height)
                if isinstance(w, MTAbstractLayout):
                    _w,_h = w.minimum_size
                    if w.size_hint[0] != None:
                        width  += _w + padding
                    if w.size_hint[1] != None:
                        height = max(_h + padding, height)

        if self.orientation == 'vertical':
            height += (len(self.children) -1) * spacing
            for w in self.children:
                if w.size_hint[0] == None:
                    width   = max(w.width + padding, width)
                if w.size_hint[1] == None:
                    height += w.height + padding
                if isinstance(w, MTAbstractLayout):
                    _w,_h = w.minimum_size
                    if w.size_hint[0] != None:
                        width   = max(_w + padding, width)
                    if w.size_hint[1] != None:
                        height += _h + padding

        self.minimum_size = (width, height)


    def do_layout(self):

        stretch_weight = [0,0]
        for w in self.children:
            stretch_weight[0] += w.size_hint[0] or 0.0
            stretch_weight[1] += w.size_hint[1] or 0.0

        if self.orientation == 'horizontal':
            x = self.padding
            stretch_space = max(0.0,self.width - self.minimum_size[0])
            for c in reversed(self.children):
                c_pos = self.x + x, self.y
                c_size = list(c.size)
                if c.size_hint[0]:
                    #its sizehint * available space
                    c_size[0] = stretch_space * c.size_hint[0]/float(stretch_weight[0])
                    if isinstance(c, MTAbstractLayout):
                        c_size[0] += c.minimum_size[0]
                if c.size_hint[1]:
                    c_size[1] = c.size_hint[1] * self.height
                self.reposition_child(c, pos=c_pos, size=c_size)
                x += c_size[0] + self.spacing
            x += self.padding

        if self.orientation == 'vertical':
            y = self.padding
            stretch_space = max(0.0,self.height - self.minimum_size[1])
            for c in self.children:
                c_pos = self.x, self.y + y
                c_size = list(c.size)
                if c.size_hint[1]:
                    c_size[1] = stretch_space * c.size_hint[1]/float(stretch_weight[1])
                    if isinstance(c, MTAbstractLayout):
                        c_size[1] += c.minimum_size[1]
                if c.size_hint[0]:
                    c_size[0] = c.size_hint[0] * self.width
                self.reposition_child(c, pos=c_pos, size=c_size)
                y += c_size[1] + self.spacing


        self.dispatch_event('on_layout')


# Register all base widgets
MTWidgetFactory.register('MTBoxLayout', MTBoxLayout)
