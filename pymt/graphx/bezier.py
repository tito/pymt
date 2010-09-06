'''
Bezier: handle curve based on bezier path


A bezier path can be constructed like this ::

    path = BezierPath()
    # start the path
    path.path_begin(x, y)
    # add a point with x1/y1, x2/y2 as control point
    path.path_curve_to(x1, y1, x2, y2, x, y)
    # repeat this multiple time... until
    # path.path_curve_to(...)
    # close the path
    path.path_close()
    # and draw !
    path.draw()


You can also provide a point list, and directly create a path ::

    points = (startx, starty,
              controlx1, controly1, controlx2, controly2, pointx1, pointx2,
              # ... repeat
    )

    path = BezierPath(path=points)
    path.draw()


'''

__all__ = ('BezierPath', )

from pymt.graphx.statement import GlDisplayList, gx_begin
from pymt.logger import pymt_logger
from pymt.graphx.draw import drawLine
from OpenGL.GL import glVertex2f
from OpenGL.GLU import gluNewTess, gluTessNormal, gluTessProperty, \
    gluTessBeginPolygon, gluTessBeginContour, gluTessEndContour, \
    gluTessEndPolygon, gluTessCallback, gluErrorString, gluTessVertex, \
    GLU_TESS_WINDING_RULE, GLU_TESS_WINDING_NONZERO, GLU_TESS_VERTEX, \
    GLU_TESS_BEGIN, GLU_TESS_END, GLU_TESS_ERROR


class BezierPath(object):
    '''Create a line based on bezier equation, or a shape using GLU tess.

    :Parameters:
        `filled` : boolean, default to False
            Create a filled bezier shape
        `path` : list, default to None
            Create a path directly from points. See up description for more
            information about the format used in path.
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('filled', False)
        kwargs.setdefault('path', None)

        self._tess                  = None
        self._filled_path           = None
        self._dl                    = GlDisplayList()
        self._path                  = []
        self._bezier_coefficients   = []
        self._bezier_points         = 10
        self._contructing           = False

        super(BezierPath, self).__init__()

        self.filled                 = kwargs.get('filled')
        self.x, self.y              = 0, 0

        if kwargs.get('path'):
            self.calculate_from_bezier_path(kwargs.get('path'))

    def path_begin(self, x, y):
        '''Start a new bezier path'''
        self._path = [x, y]
        self.x, self.y = x, y

    def path_end(self):
        '''End the current bezier path'''
        self._path += self._path[0:2]
        self.reset()

    def path_curve_to(self, x1, y1, x2, y2, x, y):
        '''Add a control point into bezier path'''
        if not self._bezier_coefficients:
            for i in xrange(self._bezier_points + 1):
                t = float(i) / self._bezier_points
                t0 = (1 - t) ** 3
                t1 = 3 * t * (1 - t) ** 2
                t2 = 3 * t ** 2 * (1 - t)
                t3 = t ** 3
                self._bezier_coefficients.append([t0, t1, t2, t3])
        for i, t in enumerate(self._bezier_coefficients):
            px = t[0] * self.x + t[1] * x1 + t[2] * x2 + t[3] * x
            py = t[0] * self.y + t[1] * y1 + t[2] * y2 + t[3] * y
            self._path += px, py
        self.x, self.y = px, py
        self.reset()

    def calculate_from_bezier_path(self, points):
        '''Create a new path from a list of control points'''
        self.path_begin(points[0], points[1])
        for i in xrange(2, len(points), 6):
            x1, y1, x2, y2, x, y = points[i:i+6]
            self.path_curve_to(x1, y1, x2, y2, x, y)
        self.path_end()
        self.reset()

    def draw_filled_path(self):
        for style, points in self.filled_path:
            with gx_begin(style):
                for x, y in zip(points[::2], points[1::2]):
                    glVertex2f(x, y)

    def draw(self):
        '''Draw the path on screen (filled or line)'''
        if not self._dl.is_compiled():
            with self._dl:
                if self.filled:
                    self.draw_filled_path()
                else:
                    drawLine(self.path)
        self._dl.draw()

    def reset(self):
        '''Reset the display list cache'''
        self._dl.clear()

    def _get_path(self):
        return self._path
    path = property(_get_path, doc='''Return the calculated path in format (x,y,x,y...)''')

    def _get_filled_path(self):
        if self._filled_path:
            return self._filled_path

        self._tess = gluNewTess()
        gluTessNormal(self._tess, 0, 0, 1)
        gluTessProperty(self._tess, GLU_TESS_WINDING_RULE, GLU_TESS_WINDING_NONZERO)

        tess_list = []

        def tess_vertex(vertex):
            self._tess_shape += list(vertex[0:2])

        def tess_begin(which):
            self._tess_style = which
            self._tess_shape = []

        def tess_end():
            tess_list.append((self._tess_style, self._tess_shape))

        def tess_error(code):
            err = gluErrorString(code)
            pymt_logger.warning('BezierPath: GLU Tesselation Error: %s' % str(err))

        gluTessCallback(self._tess, GLU_TESS_VERTEX, tess_vertex)
        gluTessCallback(self._tess, GLU_TESS_BEGIN, tess_begin)
        gluTessCallback(self._tess, GLU_TESS_END, tess_end)
        gluTessCallback(self._tess, GLU_TESS_ERROR, tess_error)

        gluTessBeginPolygon(self._tess, None)
        gluTessBeginContour(self._tess)
        for x, y in zip(self._path[::2], self._path[1::2]):
            v_data = (x, y, 0)
            gluTessVertex(self._tess, v_data, v_data)
        gluTessEndContour(self._tess)
        gluTessEndPolygon(self._tess)

        self._filled_path = tess_list
        return tess_list
    filled_path = property(_get_filled_path,
                    doc='''Return the filled shape in format ((gl style, (x,y,x,y...)),...)''')

