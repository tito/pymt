from __future__ import with_statement
from pymt import *

'''
THIS IS A WORK IN PROGRESS
Don't Touch plz :)

Thanks, tito.


'''

class HVMatrix(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('matrix_size', (3,3))
        kwargs.setdefault('spacing', 5)
        super(HVMatrix, self).__init__(**kwargs)
        self.matrix_size = kwargs.get('matrix_size')
        self.spacing = kwargs.get('spacing')
        self.dl = GlDisplayList()
        self.children_active = []

    def add_widget(self, widget, do_layout=True):
        if len(self.children) >= self.matrix_size[0] * self.matrix_size[1]:
            raise Exception('Too much children in HVMatrix. Increase your matrix_size!')
        super(HVMatrix, self).add_widget(widget)
        if do_layout:
            self.layout()

    def layout(self):
        mx, my = self.matrix_size
        spacing = self.spacing

        cols = {}
        rows = {}
        for i in range(my):
            cols[i] = 0
        for i in range(mx):
            rows[i] = 0

        # calculate rows/cols size
        i = 0
        for col in range(my):
            for row in range(mx):
                if i >= len(self.children):
                    break
                c = self.children[i]
                if c.width > cols[col]:
                    cols[col] = c.width
                if c.height > rows[row]:
                    rows[row] = c.height
                i = i + 1

        x = spacing
        y = spacing
        i = 0
        for col in range(my):
            x = spacing
            for row in range(mx):
                if i >= len(self.children):
                    break
                c = self.children[i]
                c.pos = (x, y)
                c.size = (cols[col], rows[row])
                i = i + 1
                x = x + cols[col] + spacing
            y = y + rows[row] + spacing

        self.dl.clear()

    def on_draw(self):
        if not self.dl.is_compiled():
            with self.dl:
                for w in self.children:
                    w.dispatch_event('on_draw')
        self.draw()

    def on_resize(self, w, h):
        self.layout()

    def draw(self):
        self.dl.draw()
        for w in self.children_active:
            w.dispatch_event('on_draw')

    def get_form(self):
        if self.parent:
            return self.parent.get_form()
        return None



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

class MTFormLabel(MTForm):
    def __init__(self, **kwargs):
        kwargs.setdefault('label', '')
        super(MTForm, self).__init__(**kwargs)
        self.label = kwargs.get('label')

    def _get_label(self):
        return self._label
    def _set_label(self, label):
        self._label = label
        self._label_obj = Label(text=label)
        self.size = self._label_obj.content_width, self._label_obj.content_height
    label = property(_get_label, _set_label)

    def draw(self):
        self._label_obj.x, self._label_obj.y = self.pos
        self._label_obj.draw()


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

MTWidgetFactory.register('MTForm', MTForm)
MTWidgetFactory.register('MTFormInput', MTFormInput)
MTWidgetFactory.register('MTFormLabel', MTFormLabel)
MTWidgetFactory.register('HVMatrix', HVMatrix)

xmldef = '''<?xml version="1.0" encoding="UTF-8"?>
<MTScatterPlane>
    <MTForm pos="(200,200)" padding="20">
        <HVMatrix matrix_size="(2, 4)">
            <MTFormLabel label="'Name'"/>
            <MTFormInput id="'input_name'"/>
            <MTFormLabel label="'Surname'"/>
            <MTFormInput id="'input_surname'"/>
            <MTFormLabel label="'Nickname'"/>
            <MTFormInput id="'input_nickname'"/>
            <MTFormLabel label="'Age'"/>
            <MTFormInput id="'input_age'"/>
        </HVMatrix>
    </MTForm>
</MTScatterPlane>
'''

w = MTWindow()
x = XMLWidget(xml=xmldef)
w.add_widget(x)
runTouchApp()
