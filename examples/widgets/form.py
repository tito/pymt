from __future__ import with_statement
from pymt import *

'''
THIS IS A WORK IN PROGRESS
Don't Touch plz :)

Thanks, tito.


'''

class MTGridLayout(MTAbstractLayout):
    def __init__(self, **kwargs):
        kwargs.setdefault('cols', None)
        kwargs.setdefault('rows', None)
        kwargs.setdefault('spacing', 10)
        super(MTGridLayout, self).__init__(**kwargs)
        self.cols = kwargs.get('cols')
        self.rows = kwargs.get('rows')
        self.spacing = kwargs.get('spacing')

    def get_max_widgets(self):
        if self.cols and not self.rows:
            return None
        if self.rows and not self.cols:
            return None
        return self.rows * self.cols

    def add_widget(self, widget, do_layout=True):
        max = self.get_max_widgets()
        if max and len(self.children) > max:
            raise Exception('Too much children in MTGridLayout. Increase your matrix_size!')
        super(MTGridLayout, self).add_widget(widget)

    def do_layout(self):
        spacing = self.spacing

        cols = {}
        rows = {}
        for i in range(self.cols):
            cols[i] = 0
        for i in range(self.rows):
            rows[i] = 0

        # calculate rows/cols size
        i = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if i >= len(self.children):
                    break
                c = self.children[i]
                if c.width > cols[col]:
                    cols[col] = c.width
                if c.height > rows[row]:
                    rows[row] = c.height
                i = i + 1

        i = 0
        y = self.y + spacing
        for row in range(self.rows):
            x = self.x + spacing
            for col in range(self.cols):
                if i >= len(self.children):
                    break
                c = self.children[i]
                c.pos = (x, y)
                c.size = (cols[col], rows[row])
                i = i + 1
                x = x + cols[col] + spacing
            y = y + rows[row] + spacing


        current_width = spacing * (len(cols) + 1)
        for i in cols:
            current_width += cols[i]
        current_height = spacing * (len(rows) + 1)
        for i in rows:
            current_height += rows[i]

        if current_height != self.content_height or current_width != self.content_width:
            self.content_width = current_width
            self.content_height = current_height
            self.dispatch_event('on_content_resize', self.content_width, self.content_height)


class MTFormWidget(MTWidget):
    def __init__(self, **kwargs):
        super(MTFormWidget, self).__init__(**kwargs)

    def on_resize(self, w, h):
        layout = self.get_parent_layout()
        if layout:
            layout.do_layout()
        super(MTFormWidget, self).on_resize(w, h)


class MTForm(MTFormWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('color', (.25,.25,.25,.6))
        kwargs.setdefault('layout', None)
        super(MTForm, self).__init__(**kwargs)
        self.layout = kwargs.get('layout')

    def _set_layout(self, layout):
        if hasattr(self, '_layout') and self._layout:
            super(MTForm, self).remove_widget(self._layout)
        self._layout = layout
        if self._layout:
            super(MTForm, self).add_widget(self._layout)
    def _get_layout(self):
        return self._layout
    layout = property(_get_layout, _set_layout)

    def add_widget(self, widget):
        self.layout.add_widget(widget)

    def draw(self):
        set_color(*self.color)
        drawRectangle(pos=self.pos, size=self.size)

    def get_parent_layout(self):
        return self

    def do_layout(self):
        self.size = self.layout.content_width, self.layout.content_height

    def on_move(self, x, y):
        super(MTForm, self).on_move(x, y)
        self.layout.pos = self.pos
        self.layout.do_layout()


class MTFormLabel(MTFormWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('label', '')
        super(MTFormLabel, self).__init__(**kwargs)
        self.label = kwargs.get('label')

    def _get_label(self):
        return self._label
    def _set_label(self, label):
        self._label = label
        self._label_obj = Label(text=label, bold=True)
        self.size = self._label_obj.content_width, self._label_obj.content_height
    label = property(_get_label, _set_label)

    def draw(self):
        self._label_obj.x, self._label_obj.y = self.pos
        self._label_obj.draw()


class MTFormInput(MTTextInput):
    def __init__(self, **kwargs):
        kwargs.setdefault('font_size', 16)
        super(MTFormInput, self).__init__(**kwargs)
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
        layout = self.get_parent_layout()
        if layout:
            layout.do_layout()
        super(MTFormInput, self).on_resize(w, h)


MTWidgetFactory.register('MTForm', MTForm)
MTWidgetFactory.register('MTFormInput', MTFormInput)
MTWidgetFactory.register('MTFormLabel', MTFormLabel)
MTWidgetFactory.register('MTGridLayout', MTGridLayout)

xmldef = '''<?xml version="1.0" encoding="UTF-8"?>
<MTScatterPlane>
    <MTForm pos="(200,200)" padding="20" layout="factory.get('MTGridLayout')(cols=2, rows=4)">
        <MTFormLabel label="'Name'"/>
        <MTFormInput id="'input_name'"/>
        <MTFormLabel label="'Surname'"/>
        <MTFormInput id="'input_surname'"/>
        <MTFormLabel label="'Nickname'"/>
        <MTFormInput id="'input_nickname'"/>
        <MTFormLabel label="'Age'"/>
        <MTFormInput id="'input_age'"/>
    </MTForm>
</MTScatterPlane>
'''

w = MTWindow()
x = XMLWidget(xml=xmldef)
w.add_widget(x)
runTouchApp()
