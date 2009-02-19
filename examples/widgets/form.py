from pymt import *

'''
THIS IS A WORK IN PROGRESS
Don't Touch plz :)

Thanks, tito.


'''



class MTForm(HVLayout):
    def __init__(self, **kwargs):
        kwargs.setdefault('alignment', 'vertical')
        kwargs.setdefault('invert_y', False)
        kwargs.setdefault('border_width', 0)
        kwargs.setdefault('border_color', (.1, .1, .1, .2))
        super(MTForm, self).__init__(**kwargs)
        self.border_width = kwargs.get('border_width')
        self.border_color = kwargs.get('border_color')
        self.layout()

    def draw(self):
        set_color(*self.border_color)
        if self.border_width > 0:
            glLineWidth(self.border_width)
        drawRectangle(pos=self.pos, size=self.size, style=GL_LINE_LOOP)
        set_color(*self.color)
        drawRectangle(pos=self.pos, size=self.size)

    def get_form(self):
        if self.__class__.__name__ == 'MTForm':
            return self
        if self.parent:
            return self.parent.get_form()
        return None

    def on_resize(self, w, h):
        form = self.get_form()
        if form:
            form.layout()


class MTFormInput(MTForm, MTTextInput):
    def __init__(self, **kwargs):
        kwargs.setdefault('font_size', 16)
        MTForm.__init__(self, **kwargs)
        MTTextInput.__init__(self, **kwargs)
        #super(MTForm, self).__init__(**kwargs)
        #super(MTTextInput, self).__init__(**kwargs)
        # get height of font-size
        self.label_obj.text = ' '
        self.height = self.label_obj.content_height
        self.label_obj.text = ''

    def draw(self):
        if self.state[0] == 'down':
            glColor4f(0.5,0.5,0.5,0.5)
        else:
            glColor4f(*self.color)
        drawRectangle(pos=self.pos, size=self.size)
        self.label_obj.x, self.label_obj.y = self.pos
        self.label_obj.draw()

    def on_resize(self, w, h):
        MTForm.on_resize(self, w, h)

w = MTWindow()
p = MTScatterPlane()
form = MTForm(pos=(200, 200), padding=20)
textinput = MTFormInput(color=(.5,.5,.5,.5))
form.add_widget(textinput)
textinput = MTFormInput(color=(.5,.5,.5,.5))
form.add_widget(textinput)
textinput = MTFormInput(color=(.5,.5,.5,.5))
form.add_widget(textinput)
textinput = MTFormInput(color=(.5,.5,.5,.5))
form.add_widget(textinput)
p.add_widget(form)
w.add_widget(p)

print textinput.size, textinput.pos

runTouchApp()
