import pymt
from pymt import *
from pymt.ui import *

class MTTextInput(MTButton):
    """
    A text input widget is a simple label widget that will pop up a virtual keyboard when touched
    any input of the virtual keyboard will then have effect on the TextInput widget
    """

    def __init__(self, label="text input", pos=(100,100), size=(100,100), color=(0.2,0.2,0.2,1), **kargs):
        MTButton.__init__(self,pos=pos, size=size, color=color, **kargs)
        self.keyboard = MTVKeyboard(self)
        self.label_obj = Label(text='', font_size=64, bold=True)
        self.label_obj.anchor_x = 'left'
        self.label_obj.anchor_y = 'bottom'
        self.is_active_input = False
        self.added_keyboard = False
        self.padding = 20

        self.register_event_type('on_text_change')


    def on_release(self,touchID, x, y):
        if self.is_active_input:
            self.hide_keyboard()
            self.is_active_input = False
        else:
            if not self.added_keyboard:
                self.get_parent_window().add_widget(self.keyboard)
            self.show_keyboard()
            self.is_active_input = True

    def on_text_change(self):

        self.label_obj.text = self.label
        self.label_obj.x = self.x +self.padding
        self.label_obj.y = self.y
        self.width =  self.label_obj.content_width +self.padding*2
        if self.width < 100:
            self.width = 100

    def show_keyboard(self):
        self.keyboard.show()

    def hide_keyboard(self):
        self.keyboard.hide()

    def draw(self):
        if self.state[0] == 'down':
            glColor4f(0.5,0.5,0.5,0.5)
            drawRectangle((self.x,self.y) , (self.width, self.height))
        else:
            glColor4f(*self.color)
            drawRectangle((self.x,self.y) , (self.width, self.height))
        self.label_obj.draw()





class MTHorizontalLayout(MTWidget):
    """
    MTHorizontalLayout lays out its child widgtes in horizonatl order
    x values are computed based on the widgets in front, all y values are set to the y value of the layout widget

    when a new widget is added, the widgets are layed out again (internal call to layout())
    call layout() to rearrange all child widgets

    padding determines how much space is put between the widgets

    """
    def __init__(self, pos=(0,0), padding=5):
        MTWidget.__init__(self, pos=pos)
        self.padding = padding

    def add_widget(self, widget):
        MTWidget.add_widget(self, widget)
        self.layout()

    def layout(self):
        self.children[0].x = self.x + self.padding
        self.children[0].y = self.y
        for i in range(1,len(self.children)):
            current_widgt = self.children[i]
            prev_widget   = self.children[i-1]
            current_widgt.x = prev_widget.x + prev_widget.width + self.padding
            current_widgt.y = self.y


class MTKeyButton(MTButton):
    """ Internal Class used in MTVKeyboard """
    def __init__(self, keyboard, pos=(0,0), size=(100, 100), label='', color=(0.1,0.1,0.1,0.7)):
        MTButton.__init__(self, pos=pos, size=size, color=color, label=label)
        self.keyboard = keyboard

    def on_press(self, touchID, x, y):
        self.keyboard.active_keys[self] = self

    def on_release(self, touchID, x, y):
        self.keyboard.on_key_down(self.label)
        if self.keyboard.active_keys.has_key(self):
            del self.keyboard.active_keys[self]




class MTVKeyboard(MTScatterWidget):
    """A virtual keyboard that can be scaled/roatetd/moved"""


    _row_keys = ["X1234567890+-","qwertyuiop", "asdfghjkl;", "zxcvbnm,.?"]

    def __init__(self, text_widget, pos=(0,0)):
        MTScatterWidget.__init__(self, pos=(0,0), size=(400,200))
        self._setup_keys()
        self.dl_needs_update = False
        self.display_list = glGenLists(1)
        self.update_dl()
        self.active_keys = {}
        #self.needs_update = False
        self.text_widget = text_widget

    def on_key_down(self, k_str):
        if k_str == "<-":
            self.text_widget.label = self.text_widget.label[:-1]
        elif k_str == "space":
            self.text_widget.label += " "
        else:
            self.text_widget.label = self.text_widget.label + k_str
        self.text_widget.dispatch_event('on_text_change')

    def update_dl(self):
        glNewList(self.display_list, GL_COMPILE)
        for w in self.children:
            w.dispatch_event('on_draw')
        glEndList()

    def _setup_keys(self):
        k_width = 25
        #print k_width

        for j in range(4):
            row = MTRectangularWidget(pos=(15,self.height-(j+1)*(k_width+3)), size=(363, k_width), color=(1,1,1,0))
            layout = MTHorizontalLayout(pos=(15,self.height-(j+1)*(k_width+3)),padding=3)

            #special keys on left
            if j==1:
                k_str   = ""
                k_btn   = MTKeyButton(self,label=k_str, size=(k_width*0.5, k_width))
                layout.add_widget(k_btn)
            if j==2:
                k_str   = "CL"
                k_btn   = MTKeyButton(self,label=k_str, size=(k_width, k_width))
                layout.add_widget(k_btn)
            if j==3:
                k_str   = "Shift"
                k_btn   = MTKeyButton(self,label=k_str, size=(k_width*1.5, k_width))
                layout.add_widget(k_btn)

            #regular keys
            num_keys = len(MTVKeyboard._row_keys[j])
            for i in range( num_keys ):
                k_str   = MTVKeyboard._row_keys[j][i]
                k_btn   = MTKeyButton(self,label=k_str, size=(k_width, k_width))
                layout.add_widget(k_btn)

            #special keys on right
            if j==1:
                k_str   = "<-"
                k_btn   = MTKeyButton(self,label=k_str, size=(k_width*2.5 +3, k_width))
                layout.add_widget(k_btn)
            if j==2:
                k_str   = "enter"
                k_btn   = MTKeyButton(self,label=k_str, size=(k_width*2+3, k_width))
                layout.add_widget(k_btn)
            if j==3:
                k_str   = "Shift"
                k_btn   = MTKeyButton(self,label=k_str, size=(k_width*1.5+3, k_width))
                layout.add_widget(k_btn)


            row.add_widget(layout)
            self.add_widget(row)

        space_key = MTKeyButton(self,label="space", pos=(18,self.height-5*(k_width+3)),size=(363, k_width), color=(0.1,0.1,0.1,0.7))
        self.add_widget(space_key)

    def on_draw(self):
        enable_blending()
        self.draw_children=False
        MTScatterWidget.on_draw(self)
        disable_blending()

    def draw_active_children(self):
        for key in self.active_keys:
            self.active_keys[key].draw()


    def draw(self):
        set_color(0.2,0.2,0.2,0.6)
        drawRectangle((0,0), self.size)
        glCallList(self.display_list)
        self.draw_active_children()

# Register all base widgets
MTWidgetFactory.register('MTTextInput', MTTextInput)
