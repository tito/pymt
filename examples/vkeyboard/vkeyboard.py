from pymt import *

class MTHorizontalLayout(MTWidget):

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
    def __init__(self, keyboard, pos=(0,0), size=(100, 100), label='', color=(0.1,0.1,0.1,0.7)):
        MTButton.__init__(self, pos=pos, size=size, color=color, label=label)
        self.keyboard = keyboard

    def on_press(self, touchID, x, y):
        self.keyboard.active_keys[self] = self

    def on_release(self, touchID, x, y):
        if self.keyboard.active_keys.has_key(self):
            del self.keyboard.active_keys[self]





class MTVKeyboard(MTScatterWidget):

    _row_keys = ["X1234567890+-","qwertyuiop", "asdfghjkl;", "zxcvbnm,./"]

    def __init__(self, pos=(0,0)):
        MTScatterWidget.__init__(self, pos=(0,0), size=(400,200))
        self._setup_keys()
        self.dl_needs_update = False
        self.display_list = glGenLists(1)
        self.update_dl()
        self.active_keys = {}
        #self.needs_update = False

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





if __name__ == "__main__":
    w = MTWindow()
    #w.set_fullscreen()
    kb = MTVKeyboard(pos=(100,100))
    w.add_widget(kb)
    runTouchApp()
