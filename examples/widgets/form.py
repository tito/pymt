from __future__ import with_statement
from pymt import *

'''
Work in progress
Don't touch :)
Thanks, tito.
'''

class MTGridLayout(MTAbstractLayout):
    '''Grid layout arrange item in a matrix.

    :Parameters:
        `cols` : int, default is None
            Number of columns in grid
        `rows` : int, default is None
            Number of rows in grid
        `spacing` : int, default to 1
            Spacing between widgets
        `uniform_width` : bool, default to False
            Try to have same width for all children
        `uniform_height` : bool, default to False
            Try to have same height for all children
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('cols', None)
        kwargs.setdefault('rows', None)
        kwargs.setdefault('spacing', 1)
        kwargs.setdefault('uniform_width', False)
        kwargs.setdefault('uniform_height', False)

        super(MTGridLayout, self).__init__(**kwargs)

        self.uniform_width  = kwargs.get('uniform_width')
        self.uniform_height = kwargs.get('uniform_height')
        self.cols           = kwargs.get('cols')
        self.rows           = kwargs.get('rows')
        self.spacing        = kwargs.get('spacing')

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

        cols = dict(zip(range(self.cols), [0 for x in range(self.cols)]))
        rows = dict(zip(range(self.rows), [0 for x in range(self.rows)]))

        # calculate maximum size for each columns and rows
        i = 0
        max_width = max_height = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if i >= len(self.children):
                    break
                c = self.children[i]
                if c.width > cols[col]:
                    cols[col] = c.width
                if c.height > rows[row]:
                    rows[row] = c.height
                if c.width > max_width:
                    max_width = c.width
                if c.height > max_height:
                    max_height = c.height
                i = i + 1

        # apply uniform
        if self.uniform_width:
            for col in range(self.cols):
                cols[col] = max_width
        if self.uniform_height:
            for row in range(self.rows):
                rows[row] = max_height

        # calculate width/height of content
        current_width = spacing * (len(cols) + 1)
        for i in cols:
            current_width += cols[i]
        current_height = spacing * (len(rows) + 1)
        for i in rows:
            current_height += rows[i]

        # reposition every children
        i = 0
        y = self.y + spacing
        for row in range(self.rows):
            x = self.x + spacing
            for col in range(self.cols):
                if i >= len(self.children):
                    break
                c = self.children[i]
                # special y, we inverse order of children at reposition
                c.pos = (x, self.y + current_height - rows[row] - (y - self.y))
                c.size = (cols[col], rows[row])
                i = i + 1
                x = x + cols[col] + spacing
            y = y + rows[row] + spacing

        # dispatch new content size
        self.content_size = (current_width, current_height)


class MTAbstractFormWidget(MTWidget):
    '''Abstract form widget. Base class used to implement any form widget.
    '''

    def __init__(self, **kwargs):
        if self.__class__ == MTAbstractFormWidget:
            raise NotImplementedError, 'class MTAbstractFormWidget is abstract'
        super(MTAbstractFormWidget, self).__init__(**kwargs)

    def on_resize(self, w, h):
        layout = self.get_parent_layout()
        if layout:
            layout.do_layout()
        super(MTAbstractFormWidget, self).on_resize(w, h)


class MTForm(MTAbstractFormWidget):
    '''Form container : with a basic layout, you can add form widget in it,
    and create simple container with basic event (cancel, submit...)

    :Parameters:
        `layout` : MTAbstractLayout class, default is None
            Initial layout to be used with form
    '''

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
        drawRoundedRectangle(pos=self.pos, size=self.size)

    def get_parent_layout(self):
        return self

    def do_layout(self):
        self.size = self.layout.content_width, self.layout.content_height

    def on_move(self, x, y):
        super(MTForm, self).on_move(x, y)
        self.layout.pos = self.pos
        self.layout.do_layout()


class MTFormLabel(MTAbstractFormWidget):
    '''Form label : a simple text label with aligmenent support

    :Parameters:
        `label` : str, default is ''
            Text of label
        `font_name` : str, default is None
            Font name
        `font_size` : int, default is 16
            Font size
        `font_style` : str, default is None
            Style of font, can be 'bold', 'italic', 'bolditalic'
        `font_color` : list, default is (1,1,1,1)
            Font color
        `multiline` : bool, default is False
            Indicate if label is multiline. You should indicate a width :)
        `halign` : str, default is 'center'
            Horizontal alignement, can be 'left', 'center', 'right'
        `valign` : str, default is 'center'
            Vertical alignement, can be 'top', 'center', 'bottom'
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('label', '')
        kwargs.setdefault('halign', 'center')
        kwargs.setdefault('valign', 'center')
        kwargs.setdefault('font_name', None)
        kwargs.setdefault('font_size', 12)
        kwargs.setdefault('font_style', None)
        kwargs.setdefault('font_color', (1,1,1,1))
        kwargs.setdefault('multiline', False)
        super(MTFormLabel, self).__init__(**kwargs)
        self.font_name  = kwargs.get('font_name')
        self.font_size  = kwargs.get('font_size')
        self.font_style = kwargs.get('font_style')
        self.font_color = kwargs.get('font_color')
        self.multiline  = kwargs.get('multiline')
        self.label      = kwargs.get('label')
        self.halign     = kwargs.get('halign')
        self.valign     = kwargs.get('valign')

    def _get_label(self):
        return self._label
    def _set_label(self, label):
        self._label = label
        opts = {}
        opts['anchor_y'] = 'bottom'
        if self.font_name:
            opts['font_name'] = self.font_name
        if self.font_size:
            opts['font_size'] = self.font_size
        if self.font_style:
            if self.font_style in ['italic', 'bolditalic']:
                opts['italic'] = True
            if self.font_style in ['bold', 'bolditalic']:
                opts['bold'] = True
        opts['color'] = map(lambda x: x * 255, self.font_color)
        opts['text'] = label
        if self.multiline:
            opts['multiline'] = self.multiline
            opts['width'] = self.width
            print opts

        self._label_obj = Label(**opts)
        self.size = self._label_obj.content_width, self._label_obj.content_height
    label = property(_get_label, _set_label)

    def get_content_pos(self, content_width, content_height):
        x, y = self.pos
        if self.halign == 'left':
            pass
        elif self.halign == 'center':
            x = x + (self.width - content_width) / 2
        elif self.halign == 'right':
            x = x + self.width - content_width
        if self.valign == 'top':
            y = y + self.height - content_height
        elif self.valign == 'center':
            y = y + (self.height - content_height) / 2
        elif self.valign == 'bottom':
            pass
        return (x, y)

    def draw(self):
        self._label_obj.x, self._label_obj.y = self.get_content_pos(
            self._label_obj.content_width, self._label_obj.content_height)
        self._label_obj.draw()


class MTFormButton(MTFormLabel):
    '''Form button : a simple button label with aligmenent support

    :Parameters:
        `color_down` : list, default is (.5, .5, .5, .5)
            Background color of pushed button

    :Events:
        `on_press`
            Fired when button is pressed
        `on_release`
            Fired when button is released
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('color_down', (.5, .5, .5, .5))
        super(MTFormButton, self).__init__(**kwargs)
        self.register_event_type('on_press')
        self.register_event_type('on_release')
        self._state         = ('normal', 0)
        self.color_down     = kwargs.get('color_down')

    def draw(self):
        if self._state[0] == 'down':
            glColor4f(*self.color_down)
        else:
            glColor4f(*self.color)
        drawRoundedRectangle(pos=self.pos, size=self.size)
        super(MTFormButton, self).draw()

    def get_state(self):
        return self._state[0]
    def set_state(self, state):
        self._state = (state, 0)
    state = property(get_state, set_state, doc='Sets the state of the button, "normal" or "down"')

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x, y):
            self._state = ('down', touchID)
            self.dispatch_event('on_press', touchID, x, y)
            return True

    def on_touch_move(self, touches, touchID, x, y):
        if self._state[1] == touchID and not self.collide_point(x,y):
            self._state = ('normal', 0)
            return True
        return self.collide_point(x, y)

    def on_touch_up(self, touches, touchID, x, y):
        if self._state[1] == touchID and self.collide_point(x,y):
            self._state = ('normal', 0)
            self.dispatch_event('on_release', touchID, x, y)
            return True
        return self.collide_point(x, y)


class MTFormInput(MTTextInput):
    '''Form input : a one-line text input, with virtual-keyboard support
    '''

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

class MTPopup(MTWidget):

    def __init__(self, **kwargs):
        kwargs.setdefault('title', 'Information')
        kwargs.setdefault('content', '')
        super(MTPopup, self).__init__(**kwargs)
        self.title      = kwargs.get('title')
        self.content    = kwargs.get('content')
        self.window     = None

        self.form = MTForm(layout=MTBoxLayout(
            padding=10, spacing=10, orientation='vertical',
            invert_y=True, uniform_width=True
        ))
        self.submit = MTFormButton(label='OK')
        self.submit.push_handlers(on_release=self.action_close_popup)
        self.form.add_widget(MTFormLabel(label=self.title, halign='left',
                                         font_style='bold', font_size=16))
        self.form.add_widget(MTFormLabel(label=self.content, halign='left',
                                         multiline=True, width=self.width))
        self.form.add_widget(self.submit)
        super(MTPopup, self).add_widget(self.form)

    def action_close_popup(self, touchID, x, y):
        self.parent.remove_widget(self)

    def add_widget(self, widget):
        raise Exception('MTPopup cannot have children')

    def on_touch_down(self, touches, touchID, x, y):
        super(MTPopup, self).on_touch_down(touches, touchID, x, y)
        return True

    def on_touch_move(self, touches, touchID, x, y):
        super(MTPopup, self).on_touch_move(touches, touchID, x, y)
        return True

    def on_touch_up(self, touches, touchID, x, y):
        super(MTPopup, self).on_touch_up(touches, touchID, x, y)
        return True

    def draw(self):
        w = self.get_parent_window()
        if self.form.x == 0:
            x = (w.width - self.form.width) / 2
            y = (w.height - self.form.height) / 2
            self.form.pos = (x, y)
        with gx_blending:
            glColor4f(0, 0, 0, 1)
            drawRectangle(pos=(0,0), size=w.size)



MTWidgetFactory.register('MTForm', MTForm)
MTWidgetFactory.register('MTFormInput', MTFormInput)
MTWidgetFactory.register('MTFormLabel', MTFormLabel)
MTWidgetFactory.register('MTFormButton', MTFormButton)
MTWidgetFactory.register('MTGridLayout', MTGridLayout)
MTWidgetFactory.register('MTPopup', MTPopup)

xmldef = '''<?xml version="1.0" encoding="UTF-8"?>
<MTScatterPlane>
    <MTForm pos="(200,200)"
    layout="factory.get('MTGridLayout')(spacing=20, cols=2, rows=5, uniform_height=True)">
        <MTFormLabel label="'Name'" halign="'right'"/>
        <MTFormInput id="'input_name'"/>
        <MTFormLabel label="'Surname'" halign="'right'"/>
        <MTFormInput id="'input_surname'"/>
        <MTFormLabel label="'Nickname'" halign="'right'"/>
        <MTFormInput id="'input_nickname'"/>
        <MTFormLabel label="'Age'" halign="'right'"/>
        <MTFormInput id="'input_age'"/>
        <MTFormButton label="'Send'"/>
        <MTFormButton label="'Cancel'"/>
    </MTForm>
</MTScatterPlane>
'''

w = MTWindow()
x = XMLWidget(xml=xmldef)
w.add_widget(x)
w.add_widget(MTPopup(width=300, content="Welcome to PyMT Widget Demonstration\nEnjoy this popup !"))
runTouchApp()
