'''
Grid layout: arrange widget in a grid
'''

__all__ = ['MTGridLayout']

from abstractlayout import MTAbstractLayout
from ...factory import MTWidgetFactory

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
        super(MTGridLayout, self).do_layout()

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

# Register all base widgets
MTWidgetFactory.register('MTGridLayout', MTGridLayout)
