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
        `uniform_width` : bool, default to False
            Try to have same width for all children
        `uniform_height` : bool, default to False
            Try to have same height for all children
        `invert_x` : bool, default to False
            Invert X axis
        `invert_y` : bool, default to False
            Invert Y axis
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('spacing', 1)
        kwargs.setdefault('padding', 0)
        kwargs.setdefault('uniform_width', False)
        kwargs.setdefault('uniform_height', False)
        kwargs.setdefault('invert_x', False)
        kwargs.setdefault('invert_y', False)

        if kwargs.get('orientation') not in ['horizontal', 'vertical']:
            raise Exception('Invalid orientation, only horizontal/vertical are supported')

        super(MTBoxLayout, self).__init__(**kwargs)

        self.spacing        = kwargs.get('spacing')
        self.padding        = kwargs.get('padding')
        self.orientation    = kwargs.get('orientation')
        self.uniform_width  = kwargs.get('uniform_width')
        self.uniform_height = kwargs.get('uniform_height')
        self.invert_x       = kwargs.get('invert_x')
        self.invert_y       = kwargs.get('invert_y')

    def do_layout(self):
        '''Recalculate position for every subwidget, fire
        on_layout when finished. If content size have changed,
        fire on_content_resize too. Uniform width/height are handled
        after on_content_resize.
        '''
        super(MTBoxLayout, self).do_layout()
        max_width = max_height = 0
        current_width = current_height = 0
        for w in self.children:
            try:
                if w.height > max_height:
                    max_height = w.height
                if w.width > max_width:
                    max_width = w.width
                if self.orientation == 'horizontal':
                    if current_width > 0:
                        current_width += self.spacing
                    current_width += w.width
                elif self.orientation == 'vertical':
                    if current_height > 0:
                        current_height += self.spacing
                    current_height += w.height
            except:
                pass

        # uniform
        if self.uniform_width:
            for w in self.children:
                w.width = max_width
            if self.orientation == 'horizontal':
                current_width = (len(self.children) - 1) * (max_width + self.spacing)
        if self.uniform_height:
            for w in self.children:
                w.height = max_height
            if self.orientation == 'vertical':
                current_height = (len(self.children) - 1) * (max_height + self.spacing)

        # adjust current width/height
        if self.orientation == 'horizontal':
            current_height = max_height
        elif self.orientation == 'vertical':
            current_width = max_width

        # apply double padding
        current_width += self.padding * 2
        current_height += self.padding * 2

        # reposition
        cur_x = self.x + self.padding
        cur_y = self.y + self.padding
        for w in self.children:
            try:
                if self.invert_x:
                    w.y = self.x + current_width - w.width - (cur_x - self.x)
                else:
                    w.x = cur_x
                if self.invert_y:
                    w.y = self.y + current_height - w.height - (cur_y - self.y)
                else:
                    w.y = cur_y
                if self.orientation == 'horizontal':
                    cur_x += w.width + self.spacing
                elif self.orientation == 'vertical':
                    cur_y += w.height + self.spacing
            except:
                pass

        self.content_size = (current_width, current_height)

        # XXX make it optionnal, in 0.2
        self.size = (self.content_width, self.content_height)

        # we just do a layout, dispatch event
        self.dispatch_event('on_layout')

# Register all base widgets
MTWidgetFactory.register('MTBoxLayout', MTBoxLayout)
