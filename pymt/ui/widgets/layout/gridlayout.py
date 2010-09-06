'''
Grid layout: arrange widget in a grid
'''

__all__ = ('MTGridLayout', 'GridLayoutException')

from pymt.ui.widgets.layout.abstractlayout import MTAbstractLayout

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
        #kwargs.setdefault('size_hint', (None,None))

        super(MTGridLayout, self).__init__(**kwargs)

        self.uniform_width  = kwargs.get('uniform_width')
        self.uniform_height = kwargs.get('uniform_height')
        self.cols           = kwargs.get('cols')
        self.rows           = kwargs.get('rows')
        self.spacing        = kwargs.get('spacing')
        self.size_hint = (None, None)

        if self.cols is None and self.rows is None:
            raise GridLayoutException('Need at least cols or rows restriction.')

    def get_max_widgets(self):
        if self.cols and not self.rows:
            return None
        if self.rows and not self.cols:
            return None
        return self.rows * self.cols

    def add_widget(self, widget, front=True, do_layout=None):
        smax = self.get_max_widgets()
        if smax and len(self.children) > smax:
            raise Exception('Too much children in MTGridLayout. Increase your rows/cols!')
        super(MTGridLayout, self).add_widget(widget, front=front, do_layout=do_layout)

    def update_minimum_size(self):
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

                #get needed size for that child
                c = self.children[i]
                w, h = c.size
                if isinstance(c, MTAbstractLayout):
                    w, h = c.minimum_size

                cols[col] = max(cols[col], w)
                self.max_col_width = max(max_width, cols[col])

                rows[row] = max(rows[row], h)
                self.max_row_height = max(max_height, rows[row])

                i = i + 1

        # consider uniform sizeing
        if self.uniform_width:
            for col in range(current_cols):
                cols[col] = self.max_col_width
        if self.uniform_height:
            for row in range(current_rows):
                rows[row] = self.max_row_height


        # calculate minimum width/height for this widget
        width = self.spacing * (len(cols) + 1)
        height = self.spacing * (len(rows) + 1)
        for i in cols:
            width += cols[i]
        for i in rows:
            height += rows[i]

        #remeber for layout
        self.col_widths  = cols
        self.row_heights = rows

        self.minimum_size = (width, height)


    def do_layout(self):
        if len(self.children) == 0:
            return


        spacing = self.spacing
        _x, _y = self.pos
        # reposition every child
        i = 0
        y = _y + spacing
        for row_height in self.row_heights.itervalues():
            x = _x + spacing
            for col_width in self.col_widths.itervalues():
                if i >= len(self.children):
                    break
                c = self.children[i]
                # special y, we inverse order of children at reposition
                c_pos = (x, self.top - row_height - (y - _y))
                c_size = list(self.children[i].size)
                if self.uniform_width or c.size_hint[0]:
                    c_size[0] = col_width * (c.size_hint[0] or 1.0)
                if self.uniform_height or c.size_hint[1]:
                    c_size[1] = row_height * (c.size_hint[1] or 1.0)
                self.reposition_child(c, pos=c_pos, size=c_size)
                i = i + 1
                x = x + col_width + spacing
            y = y + row_height + spacing

        self.dispatch_event('on_layout')
