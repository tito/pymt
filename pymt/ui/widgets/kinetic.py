'''
Kinetic Scrolling widget for PyMT
Initially written by Alex Teiche <xelapond@gmail.com>
'''

from pyglet import *
from pyglet.gl import *
from pyglet.text import Label
from pymt.graphx import *
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widgets.widget import MTWidget

### THIS NEEDS SERIOUS HELP IN THE COLOR DEPARTMENT ###

class MTKineticScrollText(MTWidget):
    '''Kinetic Scrolling widget
    It provides a vertical menu of items which you can
    scroll through by flicking your finger.  -*-Similar-*-
    to the one found on the iPhone.

    :Parameters:
        'bgcolor' : tuple, defaults to (.2, .4, .9)
            The background color of the widget
        'icolor' : tuple, defaults to (1, 1, 1)
            The color for the items
        'iscolor': tuple, defaults to (1, .28, 0)
            The color for an item when it is selected
        'tcolor' : tuple, defaults to (0, 0, 0)
            Color for the text
        'font' : string, defaults to 'Tahoma'
            Font Type
        'font_size' : int, defaults to 16
             Font Size
        'friction ' : float, defaults to 1.1
            The Psuedo-friction of the psuedo-kinetic scrolling.
        'items'  : list, defaults to []
            The plain-text items that you would like to have within the widget.

    When an item is tapped and the blob has moved less than 10
    pixels(so we know they aren't scrolling) it fires a 
    callback and passes the clicked text as the argument.
        

    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('bgcolor', (.2, .4, .9))
        kwargs.setdefault('icolor', (1, 1, 1))
        kwargs.setdefault('iscolor', (255, .28, 0))
        kwargs.setdefault('tcolor', (0, 0, 0))
        kwargs.setdefault('font_name', 'Tahoma')
        kwargs.setdefault('font_size', 16)
        kwargs.setdefault('friction', 1.1)
        kwargs.setdefault('items', [])

        super(MTKineticScrollText, self).__init__(**kwargs)
        self.register_event_type('on_item_select')

        self.bgcolor = kwargs.get('bgcolor')
        self.icolor = kwargs.get('icolor')
        self.iscolor = kwargs.get('iscolor')
        self.tcolor = kwargs.get('tcolor')
        self.font_name = kwargs.get('font_name')
        self.font_size = kwargs.get('font_size')
        self.friction = kwargs.get('friction')
        self.items = kwargs.get('items')

        #Item height
        self.iheight = 40
        #Item padding
        self.padding = 10
        #Holds the total height for all the items and padding
        self.theight = 0
        self._calc_theight()
        
        #Persistent label used for text rendering
        self.label = Label('', font_size=self.font_size, font_name=self.font_name)

        #Holds blobs that started on this widget, so we only react to them
        self.touchstarts = []

        #Holds the old Y value so relative can be calculated
        self.oy = 0
        #Holds the relative Y value
        self.ymot = 0
        #Holds the total movement of the blob
        self.blobrel = 0

        #Holds the currently selected item
        self.selected = None

        '''Holds the velocity after touch_up, so 
        that the menu can do its kinetic stuff'''
        self.vel = 0
        
        #Holds the total menu offset
        self.yoffset = 0

        #Holds what is happening, touching or spinning(nothing)
        self.mode = 'spinning'

    def _calc_theight(self):
        '''Takes the number of items and stuff about them in
        and sets self.theight to the total height in pixels of
        all of them'''
        self.theight = len(self.items)*(self.iheight + self.padding/2)

    def on_item_select(self, item):
        '''Prototype for callback'''
        pass

    def add(self, text):
        '''Function adds a new element to the widget.
        If this object is tapped, then a callback is
        called with the text as the argument
        '''
        #TODO:  Allow this to take arbitrary objects with a '.text' attribute

        self.list.append(text)
        self._calc_theight()

    def on_touch_down(self, touches, touchID, x, y):
        '''Callback for when a new touch appears.
        All we do here is set the friction to zero, so
        it stops as if we stopped it from spinning
        '''
        if self.collide_point(x, y):
            self.touchstarts.append(touchID)
            #If it is currently spinning down, stop it
            self.vel = 0
            self.oy = y
            self.mode = 'touching'
            #Figure out which item they are touching and select it
            #This works, if you have questions ask xelapond
            rpos = x - self.pos[0], y - self.pos[1]
            x = int(self.yoffset - rpos[1])/(self.padding/2 + self.iheight)
            index = int(abs(x))-1
            self.selected = self.items[index]

    def on_touch_move(self, touches, touchID, x, y):
        '''Callback for when a blob moves.
        Here we add the relative movement to the offset, 
        to acheive the scrolling effect
        '''
        if touchID in self.touchstarts:
            touches[touchID].motcalc()
            self.ymot = y - self.oy
            self.yoffset += self.ymot
            self.blobrel += abs(self.ymot)
            self.oy = y
            #If we moved by more then 10 pixels, deselect the selected
            if self.blobrel >= 10:
                self.selected = None

    def on_touch_up(self, touches, touchID, x, y):
        '''Callback for when the blob leaves the widget.
        Here we will set the last relative movement as
        the spin-down velocity, so it will continute to 
        spin after we let go.
        '''
        if touchID in self.touchstarts:
            self.vel = self.ymot
            self.ymot = 0
            if self.blobrel <= 10:
                #They intended on clicking the item below their finger
                #Fire a callback
                self.dispatch_event('on_item_select', self.selected)

            self.blobrel = 0
            self.mode = 'spinning'
            self.selected = None

    def draw(self):
        #Draw the background
        glColor3f(*self.bgcolor)
        drawRectangle(self.pos, self.size)

        #Move the menu by the spin-down velocity
        self.yoffset += self.vel
        #Divide the velocity by self.friction to emulate friction
        self.vel /= self.friction
        
        #This does rubberbanding
        #Trust xelapond in that all this random arithmetic kung-fu stuff works
        #If you have questions ask him
        if (self.yoffset*-1) + self.size[1] - self.iheight >= self.theight and self.mode == 'spinning':
            self.yoffset = -self.theight + self.size[1] - 1 - self.iheight
            self.vel *= -1
            self.vel /= 2
        elif self.yoffset >= self.iheight and self.mode == 'spinning':
            self.yoffset = self.iheight
            self.vel *= -1
            self.vel /= 2

        #Loop through all the items and draw them
        num = -1
        for text in self.items:
            num += 1
            #Calculate the position of the current item
            pos = [0, 0]
            #FIXME: Make this less ugly/make more sense?
            #Or we could just let it be with faith that it works and will continue to do so
            pos[1] = self.pos[1] + num*(self.iheight + self.padding/2) + self.yoffset #Y position
            pos[0] = self.pos[0] + 2

            #Calculate the position of the text within that box
            tpos = (pos[0] + 10, pos[1] + (self.iheight/2) - (self.font_size/2))
                
            #Calculate the size of the item
            size = (self.size[0] - 4, self.iheight)

            #If the item will be partially off the screen either way, then don't draw it
            #TODO:  Draw only part of it
            if pos[1] + size[1] > self.pos[1] + self.size[1]:
                break
            elif pos[1] < self.pos[1]:
                continue

            #Draw the actual item
            if str(self.selected) == str(text):
                #Its selected, make it colorful!
                glColor3f(*self.iscolor)
            else:
                glColor3f(*self.icolor)

            drawRectangle(pos, size)
            self.dtext(str(text), tpos)            

    def dtext(self, text, pos, color=(0, 0, 0, 255)):
        '''Function to draw text at a given pos.
        The Label rendered is persisten throughout the life
        of this object for latency reasons.  It is kept in
        self.label.
        '''
        self.label.text = text
        self.label.color = color
        self.label.x, self.label.y = pos
        self.label.draw()

MTWidgetFactory.register('MTKineticScrollText', MTKineticScrollText)

if __name__ == '__main__':
    from pymt import *

    #A random list of stuff that was in my head at the time
    list = ['Hello', 'World', 'Foo', 'bar', 'biz', 'Emacs!', 'Python!', 'PyMT!', 'Lambda!', 'IRC!', '#pymt', 'Freenode.net!', 'xmonad!']

    def on_item_select(v):
        print v

    w = MTWindow(fullscreen=False)
    wsize = w.size
    mms = MTKineticScrollText(pos=(20,20), size=(200, 400), items=list)
    mms.push_handlers('on_item_select', on_item_select)
    w.add_widget(mms)
    runTouchApp()

