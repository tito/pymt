'''
ScreenLayout: display only one widget in fullscreen at time
'''

__all__ = ('MTScreenLayout', )

from pymt.ui.widgets.layout.abstractlayout import MTAbstractLayout
from pymt.ui.widgets.layout.boxlayout import MTBoxLayout
from pymt.utils import SafeList, curry
from pymt.base import getFrameDt
from pymt.graphx import set_color, drawRectangle
from pymt.ui.widgets.button import MTButton


class MTScreenLayout(MTAbstractLayout):
    '''Base class to handle a list of screen (widgets).
    One child widget is shown at a time.

    :Parameters:
        `show_tabs`: bool, default to False
            If True, show tabs (useful for debugging)
        `duration`: float, default to 1.
            Duration to switch between screen

    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('show_tabs', False)
        kwargs.setdefault('duration', 1.)
        super(MTScreenLayout, self).__init__(**kwargs)
        self.screens = SafeList()
        self.screen = None
        self.previous_screen = None
        self._switch_t = 1.1
        self.duration = kwargs.get('duration')

        self.container = MTBoxLayout(orientation='vertical')
        super(MTScreenLayout, self).add_widget(self.container)

        self.tabs = self.new_tab_layout()
        self._show_tabs  = False
        self.show_tabs = kwargs.get('show_tabs', False)

    def _get_show_tabs(self):
        return self._show_tabs
    def _set_show_tabs(self, x):
        if self._show_tabs and x is False:
            self.container.remove_widget(self.tabs)
        if x and self._show_tabs is False:
            self.container.add_widget(self.tabs)
        self._show_tabs = x
    show_tabs = property(_get_show_tabs, _set_show_tabs)


    def new_tab_layout(self):
        '''called in init, to create teh layout in which all teh tabs are put.  overwrite to create custom tab layout
        (default is box layout, vertical, height=50, with horizontal stretch.)'''
        return MTBoxLayout(size_hint=(1.0, None), height=50)

    def new_tab(self, label):
        '''fucntion that returns a new tab.  return value must be of type MTButton or derive from it (must have on_press handler) if you overwrite the method.
        A Screenlayuot subclasses can overwrite this to create tabs based with own look and feel or do other custom things when a new tab is created'''
        return MTButton(label=label, size_hint=(1, 1), height=30)

    def add_widget(self, widget, tab_name=None):
        if tab_name:
            tab_btn = self.new_tab(tab_name)
            tab_btn.push_handlers(on_press=curry(self.select, widget))
            self.tabs.add_widget(tab_btn)
            if widget.id is None:
                widget.id = tab_name
        self.screens.append(widget)

    def remove_widget(self, widget):
        for btn in self.tabs.children[:]:
            if isinstance(widget, basestring):
                if btn.label == widget:
                    self.tabs.remove_widget(btn)
                    break
            elif btn.label == widget.id or (
                hasattr(widget, 'title') and btn.label == widget.title):
                self.tabs.remove_widget(btn)
                break
        if widget in self.screens:
            self.screens.remove(widget)

    def select(self, wid, *args):
        '''
        Select which screen is to be the current one.
        pass either a widget that has been added to this layout, or its id

        This function return True if the screen is selected, of False if we
        can't select the screen (non existant)
        '''
        if self.screen is not None:
            self.container.remove_widget(self.screen)
            self.previous_screen = self.screen
            self._switch_t = -1.0
        for screen in self.screens:
            if screen.id == wid or screen == wid:
                self.screen = screen
                self.container.add_widget(self.screen, do_layout=True)
                self.screen.parent = self
                return True
        return False


    def draw_transition(self, t):
        '''
        Function is called each frame while switching screens and
        responsible for drawing transition state.
        t will go from -1.0 (previous screen), to 0 (rigth in middle),
        until 1.0 (last time called before giving new screen full controll)
        '''
        set_color(*self.style['bg-color']) #from 1 to zero
        drawRectangle(pos=self.container.pos, size=self.container.size)
        r, g, b = self.style['bg-color'][0:3]
        if t < 0:
            if self.previous_screen is not None:
                self.previous_screen.dispatch_event('on_draw')
            set_color(r, g, b, 1+t) #from 1 to zero
            drawRectangle(pos=self.container.pos, size=self.container.size)
        else:
            if self.previous_screen is not None:
                self.screen.dispatch_event('on_draw')
            set_color(r, g, b, 1-t) #from 0 to one
            drawRectangle(pos=self.container.pos, size=self.container.size)

    def on_update(self):
        if not self.screen and len(self.screens):
            self.select(self.screens[0])
        super(MTScreenLayout, self).on_update()

    def on_draw(self):
        super(MTScreenLayout, self).on_draw()
        if self._switch_t < 1.0:
            if self.duration == 0:
                self._switch_t = 1.
            else:
                self._switch_t += getFrameDt() / self.duration
            self.draw_transition(self._switch_t)
