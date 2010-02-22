__all__ = ('MTScreenLayout', )

from abstractlayout import MTAbstractLayout
from ...factory import MTWidgetFactory
from ....utils import SafeList
from ....base import getFrameDt
from ....graphx import set_color, drawRectangle


class MTScreenLayout(MTAbstractLayout):
    '''Base class to handle a list of screen (widgets). One child widget is shown at a time.
    '''

    def __init__(self, **kwargs):
        super(MTScreenLayout, self).__init__(**kwargs)
        self.screens = SafeList()
        self.screen = None
        self.previous_screen = None
        self.switch_t = 1.1

    def add_widget(self, widget):
        self.screens.append(widget)
        if not self.screen:
            self.select(widget)

    def remove_widget(self, widget):
        self.screens.remove(widget)

    def select(self, id):
        '''
        select which screen is to be teh current one.
        pass either a widget that has been added to this layout, or its id
        '''
        if self.screen is not None:
            super(MTScreenLayout, self).remove_widget(self.screen)
            self.previous_screen = self.screen
            self.switch_t = -1.0
        for screen in self.screens:
            if screen.id == id or screen == id:
                self.screen = screen
                super(MTScreenLayout, self).add_widget(self.screen)
                return
        pymt_logger.Warning('Invalid screen or screenname, doing nothing...')

    
    def draw_transition(self, t):
        '''
        is called each frame while switching screens and responsible for drawing transition state.
        t will go from -1.0 (previous screen), to 0 (rigth in middle),
        until 1.0 (last time called before giving new screen full controll)
        '''
        r,g,b,a = self.style['bg-color']
        if t < 0:
            if self.previous_screen is not None:
                self.previous_screen.dispatch_event('on_draw')
            set_color(r,g,b,1+t) #from 1 to zero
            drawRectangle(size=self.size)
        else:
            if self.previous_screen is not None:
                self.screen.dispatch_event('on_draw')
            set_color(r,g,b,1-t) #from 0 to one
            drawRectangle(pos=self.pos, size=self.size)


    def on_draw(self):
        self.draw()
        if self.switch_t < 1.0:
            self.switch_t += getFrameDt()
            self.draw_transition(self.switch_t)
        else:
            super(MTScreenLayout, self).on_draw()

        


# Register all base widgets
MTWidgetFactory.register('MTScreenLayout', MTScreenLayout)