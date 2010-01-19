'''
Side panel: a panel widget that attach to a side of the screen
'''

__all__ = ('MTSidePanel', )

from ...graphx import drawCSSRectangle, set_color
from ..factory import MTWidgetFactory
from ..animation import Animation
from widget import MTWidget

class MTSidePanel(MTWidget):
    '''A panel widget that attach to a side of the screen
    (similar to gnome-panel for linux user).

    :Parameters:
        `align` : str, default to 'center'
            Alignement on the side. Can be one of
            'left', 'right', 'top', 'bottom', 'center', 'middle'.
            For information, left-bottom, center-middle, right-top have the
            same meaning.
        `corner` : MTWidget object, default to None
            Corner object to use for pulling in/out the layout. If None
            is provided, the default will be a MTButton() with appropriate
            text label (depend of side)
        `corner_size` : int, default to 30
            Size of the corner, can be the width or height, it depend of side.
        `duration` : float, default to 0.5
            Animation duration for pull in/out
        `hide` : bool, default to True
            If true, the widget will be hide by default, otherwise,
            the panel is showed
        `layout` : AbstractLayout object, default to None
            Layout to use inside corner widget. If None is provided,
            the default will be a MTBoxLayout() with default parameters
        `side` : str, default to 'left'
            Side to attach the widget. Can be one of 
            'left', 'right', 'top', 'bottom'.
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('side', 'left')
        kwargs.setdefault('align', 'center')
        kwargs.setdefault('layout', None)
        kwargs.setdefault('corner_size', 30)
        kwargs.setdefault('corner', None)
        kwargs.setdefault('hide', True)
        kwargs.setdefault('duration', .5)

        assert(kwargs.get('side') in ('bottom', 'top', 'left', 'right'))
        assert(kwargs.get('align') in ('bottom', 'top', 'left', 'right', 'middle', 'center'))

        super(MTSidePanel, self).__init__(**kwargs)

        self.side        = kwargs.get('side')
        self.align       = kwargs.get('align')
        self.corner_size = kwargs.get('corner_size')
        self.duration    = kwargs.get('duration')
        layout           = kwargs.get('layout')
        corner           = kwargs.get('corner')

        if layout is None:
            from layout import MTBoxLayout
            layout = MTBoxLayout()
        self.layout = layout
        super(MTSidePanel, self).add_widget(layout)

        if corner is None:
            from button import MTButton
            if self.side == 'right':
                label = '<'
            elif self.side == 'left':
                label = '>'
            elif self.side == 'top':
                label = 'v'
            elif self.side == 'bottom':
                label = '^'
            corner = MTButton(label=label)
        self.corner = corner
        super(MTSidePanel, self).add_widget(self.corner)
        self.corner.connect('on_press', self._corner_on_press)

        self.initial_pos    = self.pos
        self.layout_visible = True
        self.need_reposition = True

        if kwargs.get('hide'):
            self.hide()

    def add_widget(self, widget):
        self.layout.add_widget(widget)

    def remove_widget(self, widget):
        self.layout.remove_widget(widget)

    def _corner_on_press(self, *largs):
        if self.layout_visible:
            self.hide()
        else:
            self.show()
        return True

    def show(self):
        dpos = self.initial_pos
        self.layout.do(Animation(duration=self.duration, f='ease_out_cubic', pos=dpos))
        self.layout_visible = True

    def hide(self):
        self.layout_visible = False
        w = self.get_parent_window()
        if not w:
            return
        if self.side == 'left':
            dpos = (-self.layout.width, self.y)
        elif self.side == 'right':
            dpos = (w.width, self.y)
        elif self.side == 'top':
            dpos = (self.x, w.height)
        elif self.side == 'bottom':
            dpos = (self.x, -self.layout.height)
        self.layout.do(Animation(duration=self.duration, f='ease_out_cubic', pos=dpos))

    def on_update(self):
        w = self.get_parent_window()

        # first execution, need to place layout in the good size
        if self.need_reposition:
            if self.layout_visible:
                if self.side == 'right':
                    self.layout.x = w.width - self.layout.width
                elif self.side == 'top':
                    self.layout.y = w.height - self.layout.height
                elif self.side == 'left':
                    self.layout.x = 0
                elif self.side == 'bottom':
                    self.layout.y = 0
            else:
                if self.side == 'left':
                    dpos = (-self.layout.width, self.y)
                elif self.side == 'right':
                    dpos = (w.width, self.y)
                elif self.side == 'top':
                    dpos = (self.x, w.height)
                elif self.side == 'bottom':
                    dpos = (self.x, -self.layout.height)
                self.layout.pos = dpos
            self.need_reposition = False

        # adjust size + configure position
        if self.side in ('left', 'right'):
            self.corner.size = (self.corner_size, self.layout.height)
            if self.align in ('bottom', 'left'):
                cy = 0
            elif self.align in ('top', 'right'):
                cy = w.height - self.layout.height
            elif self.align in ('center', 'middle'):
                cy = w.center[1] - self.layout.height / 2.
            self.layout.y = cy
        elif self.side in ('top', 'bottom'):
            self.corner.size = (self.layout.width, self.corner_size)
            if self.align in ('bottom', 'left'):
                cx = 0
            elif self.align in ('top', 'right'):
                cx = w.width - self.layout.width
            elif self.align in ('center', 'middle'):
                cx = w.center[0] - self.layout.width / 2.
            self.layout.x = cx
        if self.side == 'left':
            cx = self.layout.x + self.layout.width
        elif self.side == 'right':
            cx = self.layout.x - self.corner_size
        elif self.side == 'top':
            cy = self.layout.y - self.corner_size
        elif self.side == 'bottom':
            cy = self.layout.y + self.layout.height

        # place corner :)
        self.corner.pos  = (cx, cy)
        super(MTSidePanel, self).on_update()

    def on_move(self, x, y):
        self.initial_pos = x, y
        self.layout.pos  = x, y

    def draw(self):
        set_color(*self.style.get('bg-color'))
        drawCSSRectangle(pos=self.layout.pos, size=self.layout.size, style=self.style)

    # optimization

    def on_touch_down(self, touch):
        if self.corner.dispatch_event('on_touch_down', touch):
            return True
        return super(MTSidePanel, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.corner.dispatch_event('on_touch_move', touch):
            return True
        return super(MTSidePanel, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.corner.dispatch_event('on_touch_up', touch):
            return True
        return super(MTSidePanel, self).on_touch_up(touch)

# Register all base widgets
MTWidgetFactory.register('MTSidePanel', MTSidePanel)
