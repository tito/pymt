'''
Grid layout: arrange widget in a grid
'''

__all__ = ('MTGridLayout', 'GridLayoutException')

from abstractlayout import MTAbstractLayout
from ...factory import MTWidgetFactory

class GridLayoutException(Exception):
    pass

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

        if self.cols is None and self.rows is None:
            raise GridLayoutException('Need at least cols or rows restriction.')

    def get_max_widgets(self):
        if self.cols and not self.rows:
            return None
        if self.rows and not self.cols:
            return None
        return self.rows * self.cols

    def add_widget(self, widget, do_layout=None):
        max = self.get_max_widgets()
        if max and len(self.children) > max:
            raise Exception('Too much children in MTGridLayout. Increase your matrix_size!')
        super(MTGridLayout, self).add_widget(widget, do_layout=do_layout)

    def reposition_child(self, child, pos=None, size=None):
        if pos:
            child.pos = pos
        if size:
            child.size = size

    def do_layout(self):
        super(MTGridLayout, self).do_layout()

        # no children, no layout :)
        if len(self.children) == 0:
            return

        spacing = self.spacing

        current_cols = self.cols
        current_rows = self.rows
        if current_cols is None:
            current_cols = 1 + (len(self.children) / current_rows)
        elif current_rows is None:
            current_rows = 1 + (len(self.children) / current_cols)

        cols = dict(zip(xrange(current_cols), [0] * current_cols))
        rows = dict(zip(xrange(current_rows), [0] * current_rows))

        # calculate maximum size for each columns and rows
        i = 0
        max_width = max_height = 0
        for row in range(current_rows):
            for col in range(current_cols):
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
            for col in range(current_cols):
                cols[col] = max_width
        if self.uniform_height:
            for row in range(current_rows):
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
        for row in range(current_rows):
            x = self.x + spacing
            for col in range(current_cols):
                if i >= len(self.children):
                    break
                c = self.children[i]
                # special y, we inverse order of children at reposition
                c_pos = (x, self.y + current_height - rows[row] - (y - self.y))
                c_size = list(self.children[i].size)
                if self.uniform_width and self.uniform_height:
                    c_size = (cols[col], rows[row])
                elif self.uniform_width:
                    c_size[0] = cols[col]
                elif self.uniform_height:
                    c_size[1] = rows[row]
                self.reposition_child(c, pos=c_pos, size=c_size)
                i = i + 1
                x = x + cols[col] + spacing
            y = y + rows[row] + spacing

        # dispatch new content size
        self.content_size = (current_width, current_height)

        # XXX make it optionnal, in 0.2
        self.size = (self.content_width, self.content_height)

        # we just do a layout, dispatch event
        self.dispatch_event('on_layout')

# Register all base widgets
MTWidgetFactory.register('MTGridLayout', MTGridLayout)
