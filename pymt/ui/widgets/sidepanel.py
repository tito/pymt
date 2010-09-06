'''
Side panel: a panel widget that attach to a side of the screen
'''

__all__ = ('MTSidePanel', )

from pymt.graphx import drawCSSRectangle, set_color
from pymt.ui.animation import Animation
from pymt.ui.widgets.widget import MTWidget

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
        kwargs.setdefault('hide', True)

        super(MTSidePanel, self).__init__(**kwargs)

        self.side        = kwargs.get('side', 'left')
        self.align       = kwargs.get('align', 'center')
        self.corner_size = kwargs.get('corner_size', 30)
        self.duration    = kwargs.get('duration', .5)
        layout           = kwargs.get('layout', None)
        corner           = kwargs.get('corner', None)

        assert(self.side in ('bottom', 'top', 'left', 'right'))
        assert(self.align in ('bottom', 'top', 'left', 'right', 'middle', 'center'))

        if layout is None:
            from pymt.ui.widgets.layout import MTBoxLayout
            layout = MTBoxLayout()
        self.layout = layout
        super(MTSidePanel, self).add_widget(layout)

        if corner is None:
            from pymt.ui.widgets.button import MTButton
            if self.side == 'right':
                label = '<'
            elif self.side == 'left':
                label = '>'
            elif self.side == 'top':
                label = 'v'
            elif self.side == 'bottom':
                label = '^'
            corner = MTButton(label=label)
        else:
            self.corner_size = None
        self.corner = corner
        # Don't add to front or widgets added as children of layout will be occluded
        super(MTSidePanel, self).add_widget(self.corner, front=False)
        self.corner.connect('on_press', self._corner_on_press)

        self.initial_pos = self.pos
        self.need_reposition = True

        if kwargs.get('hide'):
            self.layout.visible = False
            self.hide()

    def add_widget(self, widget):
        self.layout.add_widget(widget)

    def remove_widget(self, widget):
        self.layout.remove_widget(widget)

    def _corner_on_press(self, *largs):
        if self.layout.visible:
            self.hide()
        else:
            self.show()
        return True

    def show(self):
        dpos = self._get_position_for(True)
        self.layout.visible = True
        self.layout.do(Animation(duration=self.duration, f='ease_out_cubic', pos=dpos))

    def _on_animation_complete_hide(self, *largs):
        self.layout.visible = False

    def hide(self):
        dpos = self._get_position_for(False)
        if dpos is None:
            return
        anim = Animation(duration=self.duration, f='ease_out_cubic', pos=dpos)
        anim.connect('on_complete', self._on_animation_complete_hide)
        self.layout.do(anim)

    def _get_position_for(self, visible):
        # get position for a specific state (visible or not visible)
        w = self.get_parent_window()
        if not w:
            return

        side = self.side
        x = self.layout.x
        y = self.layout.y
        if visible:
            if side == 'right':
                x = w.width - self.layout.width
            elif side == 'top':
                y = w.height - self.layout.height
            elif side == 'left':
                x = 0
            elif side == 'bottom':
                y = 0
        else:
            if side == 'left':
                x, y = (-self.layout.width, self.y)
            elif side == 'right':
                x, y = (w.width, self.y)
            elif side == 'top':
                x, y = (self.x, w.height)
            elif side == 'bottom':
                x, y = (self.x, -self.layout.height)
        return x, y

    def on_update(self):
        w = self.get_parent_window()
        side = self.side
        align = self.align

        # first execution, need to place layout in the good size
        if self.need_reposition:
            dpos = self._get_position_for(self.layout.visible)
            self.layout.pos = dpos
            self.need_reposition = False

        # adjust size + configure position
        cw, ch = self.corner.size
        if side in ('left', 'right'):
            if self.corner_size is not None:
                self.corner.size = (self.corner_size, self.layout.height)
            if align in ('bottom', 'left'):
                cy = ly = 0
            elif align in ('top', 'right'):
                ly = w.height - self.layout.height
                cy = w.height - ch
            elif align in ('center', 'middle'):
                ly = w.center[1] - self.layout.height / 2.
                cy = w.center[1] - ch / 2.
            self.layout.y = ly
        elif side in ('top', 'bottom'):
            if self.corner_size is not None:
                self.corner.size = (self.layout.width, self.corner_size)
            if align in ('bottom', 'left'):
                cx = lx = 0
            elif align in ('top', 'right'):
                lx = w.width - self.layout.width
                cx = w.width - cw
            elif align in ('center', 'middle'):
                lx = w.center[0] - self.layout.width / 2.
                cx = w.center[0] - cw / 2.
            self.layout.x = lx
        if side == 'left':
            cx = self.layout.x + self.layout.width
        elif side == 'right':
            cx = self.layout.x - self.corner.width
        elif side == 'top':
            cy = self.layout.y - self.corner.height
        elif side == 'bottom':
            cy = self.layout.y + self.layout.height

        # place corner :)
        self.corner.pos  = (cx, cy)
        super(MTSidePanel, self).on_update()

    def on_move(self, x, y):
        self.initial_pos = x, y
        self.layout.pos  = x, y

    def draw(self):
        if not self.layout.visible:
            return
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
