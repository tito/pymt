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

        self.skip_update = False #needed to prevent update based on own resize
        super(MTBoxLayout, self).__init__(**kwargs)

        self.spacing        = kwargs.get('spacing')
        self.padding        = kwargs.get('padding')
        self.uniform_width  = kwargs.get('uniform_width')
        self.uniform_height = kwargs.get('uniform_height')
        self.invert_x       = kwargs.get('invert_x')
        self.invert_y       = kwargs.get('invert_y')
        self.orientation    = kwargs.get('orientation')
        
        
    def _get_orientation(self):
        return self._orientation
    def _set_orientation(self, orientation):
        if orientation in ['horizontal', 'vertical']:
            self._orientation = orientation
            self.need_layout = True
            self.do_layout()
        else:
            raise ValueError("'%s' is not a valid orientation for BoxLayout!  Allowed values are: 'horizontal' and 'vertical'." % anchor)
    orientation = property(_get_orientation, _set_orientation, doc="Orientation of widget inside layout, can be `horizontal` or `vertical`")

    def do_layout(self):
        '''Recalculate position for every subwidget, fire
        on_layout when finished. If content size have changed,
        fire on_content_resize too. Uniform width/height are handled
        after on_content_resize.
        '''
        self.need_layout = False
        if self.skip_update:
            self.skip_update = False
            return
        
        super(MTBoxLayout, self).do_layout()
        max_width = max_height = 0
        current_width = current_height = 0
        total_stretch_x = 0
        total_stretch_y = 0
        widgets_to_stretch = {}
        
        if self.orientation == 'horizontal':
            for w in self.children:
                sx,sy = w.size_hint
                if sx or sy:
                    widgets_to_stretch[w] = w
                    total_stretch_x += sx or 0
                    total_stretch_y = max(total_stretch_y, sy or 0)
                else:
                    max_width = max(w.width, max_width)
                    if current_width > 0:  current_width += self.spacing
                    current_width += w.width
        elif self.orientation == 'vertical':
            for w in self.children:
                sx,sy = w.size_hint
                if sx or sy:
                    widgets_to_stretch[w] = w
                    total_stretch_x += max(total_stretch_x, sx or 0)
                    total_stretch_y = sy or 0
                else:
                    max_height = max (w.height, max_height)
                    if current_height > 0: current_height += self.spacing
                    current_height += w.height
        

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


        #use size_hints of widgets to resize them if they want
        normalized_stretch_x = 1.0 if (total_stretch_x< 1.0) else 1.0/max(total_stretch_x,0.00000001)
        normalized_stretch_y = 1.0 if (total_stretch_y< 1.0) else 1.0/max(total_stretch_y,0.00000001)
        biggest_width   = self.width * total_stretch_x*normalized_stretch_x    #biggest we migth get
        biggest_height   = self.height * total_stretch_y*normalized_stretch_y
        available_width = max(0, biggest_width - current_width) #how much we dhave left, if we did that
        available_height = max(0, biggest_height - current_height)  
        for w in widgets_to_stretch:
            sx,sy = w.size_hint
            if self.orientation == 'horizontal':
                if sx:  w.width  = sx*available_width/float(total_stretch_x)
                if sy:  w.height = sy*available_height
            elif self.orientation == 'vertical':
                if sx:  w.width  = sy*available_width
                if sy:  w.height = sy*available_height/float(total_stretch_y)

            
        
        # reposition
        cur_x = self.x + self.padding
        cur_y = self.y + self.padding
        total_width = self.padding*2
        total_height = self.padding*2
        for w in self.children:
            new_x = cur_x
            new_y = cur_y
            self.reposition_child(w, pos=(new_x, new_y))
               
            if self.orientation == 'horizontal':
                cur_x += w.width + self.spacing
                total_width += w.width + self.spacing
                total_height = max(total_height,w.height)
            elif self.orientation == 'vertical':
                cur_y += w.height + self.spacing
                total_height += w.height + self.spacing
                total_width = max(total_width,w.width)
        total_width  -= self.spacing
        total_height -= self.spacing
        
        #set own size first.  content size change might trigger parent layout, which will need correct size info
        self.skip_update = True
        self.size = (total_width, total_height)
        self.skip_update = True
        self.content_size = (total_width, total_height)
    
        # we just do a layout, dispatch event
        self.dispatch_event('on_layout')

# Register all base widgets
MTWidgetFactory.register('MTBoxLayout', MTBoxLayout)
