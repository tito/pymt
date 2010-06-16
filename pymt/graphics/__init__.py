'''
Graphics: all low level function to draw object in OpenGL.

Previous version of graphx was rely on Immediate mode of OpenGL. Immediate mode
is not anymore allowed in OpenGL 3.0, and OpenGL ES.
This graphics module is the new and stable way to draw every elements inside
PyMT. We hardly ask you to use theses class !


User mode
---------

For every object you want do draw on screen, you must create them before
drawing, on a canvas object. The Canvas object is a class that will store
all your graphics elements, and draw them. With this method, canvas can do some
optimization and avoid repetitive colors.

    canvas = Canvas()
    canvas.color(1, 0, 0, 1)
    canvas.line([50, 50, 100, 100])

Then, to draw the canvas ::

    canvas.draw()

You can also get any object instance from canvas, for later change :

    myline = canvas.line([50, 50, 100, 100])
    myline.points += [0, 150]


Expert mode
-----------

You can create your own graphic object. However, it's not recommanded to not use
canvas object.

An example with a line ::

    # in init function
    line = Line([50, 50, 100, 100])

    # in draw function
    line.draw()

    # If you want to change point of the line later, you can do
    line.points = [80, 80, 100, 100]

    # Or even add points into the line
    line.points += [58, 35]


An example with a rectangle ::

    # in init function
    rect = Rectangle(pos=(50, 50), size=(200, 200))

    # in draw function
    rect.draw()

    # You can change pos, size...
    rect.pos = (10, 10)
    rect.size = (999, 999)

An example with a rectangle + texture ::

    # in init function
    img = Image('test.png')
    rect = Rectangle(size=(100, 100), texture=img.texture)

    # in draw function
    rect.draw()

'''

from pymt import BaseObject, Texture, TextureRegion
from math import sin, cos, sqrt, pi
from array import array
from statement import gx_texture
from OpenGL.arrays import vbo
from OpenGL.GL import *

#
# Documentation:
#  http://www.opengl.org/wiki/Vertex_Buffer_Object
#
# Format:
#  v = Vertex (vv = xy, vvv = xyz)
#  c = Color (ccc = rgb, cccc = rgba)
#  t = Texture (tt = uv, ttt = uvw)
#  n = Normal (nn = xy, nnn = xyz)
#  i = Index
#  e = Edge
#
_pointers_gl = {
    'v': (glVertexPointer, GL_VERTEX_ARRAY),
    'c': (glColorPointer, GL_COLOR_ARRAY),
    't': (glTexCoordPointer, GL_TEXTURE_COORD_ARRAY),
    'n': (glNormalPointer, GL_NORMAL_ARRAY),
    'e': (glEdgeFlagPointer, GL_EDGE_FLAG_ARRAY),
    'i': (glIndexPointer, GL_INDEX_ARRAY),
}

_type_gl = {
    'points': GL_POINTS,
    'lines': GL_LINES,
    'line_loop': GL_LINE_LOOP,
    'line_strip': GL_LINE_STRIP,
    'triangles': GL_TRIANGLES,
    'triangle_fan': GL_TRIANGLE_FAN,
    'triangle_strip': GL_TRIANGLE_STRIP,
    'quads': GL_QUADS,
    'quad_strip': GL_QUAD_STRIP,
    'polygon': GL_POLYGON
}

class GraphicContext(object):
    '''Handle the saving/restore of the context

    TODO: explain more how it works
    '''
    __slots__ = ('state', 'stack', 'journal')
    def __init__(self):
        super(GraphicContext, self).__init__()
        self.state = {}
        self.stack = []
        self.journal = {}

        # create initial state
        self.reset()
        self.save()

    def __getattr__(self, attr):
        if attr in GraphicContext.__slots__:
            return super(GraphicContext, self).__getattribute__(attr)
        return super(GraphicContext, self).__getattribute__('state')[attr]

    def __setattr__(self, attr, value):
        if attr in GraphicContext.__slots__:
            super(GraphicContext, self).__setattr__(attr, value)
        else:
            # save into the context
            super(GraphicContext, self).__getattribute__('state')[attr] = value
            # save into the journal for a futur play
            super(GraphicContext, self).__getattribute__('journal')[attr] = True

    def reset(self):
        self.color = (1, 1, 1, 1)
        self.blend = False
        self.blend_sfactor = GL_SRC_ALPHA
        self.blend_dfactor = GL_ONE_MINUS_SRC_ALPHA
        self.linewidth = 1

    def save(self):
        self.stack.append(self.state.copy())

    def restore(self):
        newstate = self.stack.pop()
        state = self.state
        set = self.__setattr__
        for k, v in newstate.items():
            if state[k] != v:
                set(k, v)

    def flush(self):
        # activate all the last changes done on context
        # apply all the actions in the journal !
        if not len(self.journal):
            return
        state = self.state
        journal = self.journal
        for x in journal.keys():
            value = state[x]
            if x == 'color':
                glColor4f(*value)
            elif x == 'blend':
                if value:
                    glEnable(GL_BLEND)
                else:
                    glDisable(GL_BLEND)
            elif x in ('blend_sfactor', 'blend_dfactor'):
                glBlendFunc(state['blend_sfactor'], state['blend_dfactor'])
            elif x == 'linewidth':
                glLineWidth(value)
        journal.clear()


#: Default canvas used in graphic element
default_context = GraphicContext()

class GraphicInstruction(object):
    __slots__ = ('context', )
    def __init__(self):
        super(GraphicInstruction, self).__init__()
        self.context = default_context
    def draw(self):
        '''Draw/Execute the graphical element on screen'''
        pass

class GraphicContextSave(GraphicInstruction):
    def draw(self):
        self.context.save()

class GraphicContextRestore(GraphicInstruction):
    def draw(self):
        self.context.restore()

class GraphicContextChange(GraphicInstruction):
    __slots__ = ('instructions', )
    def __init__(self, **kwargs):
        super(GraphicContextChange, self).__init__()
        self.instructions = kwargs
    def draw(self):
        for k, v in self.instructions.iteritems():
            setattr(self.context, k, v)

class GraphicElement(GraphicInstruction):
    '''
    This is the lowest graphical element you can use. It's an abstraction to
    Vertex Buffer Object, and you can push your vertex, color, texture ... and
    draw them easily.

    The format of the buffer is specified in characters code. For example,
    'vvcccc' mean you'll have 2 vertex + 4 colors coordinates.
    You have 6 differents components that you can use:
        * v: vertex
        * c: color
        * t: texture
        * n: normal
        * i: index (not yet used)
        * e: edge (not yet used)

    For each component, VBO are separated.

    :Parameters:
        `format`: string, default to None
            The format must be specified at start, and cannot be changed once
            the graphic is created.
        `type`: string, default to None
            Specify how the graphic will be drawed. One of: 'lines',
            'line_loop', 'line_strip', 'triangles', 'triangle_fan',
            'triangle_strip', 'quads', 'quad_strip', 'points', 'polygon'
        `usage`: string, default to 'GL_DYNAMIC_DRAW'
            Specify the usage of VBO. Can be one of 'GL_STREAM_DRAW',
            'GL_STREAM_READ', 'GL_STREAM_COPY', 'GL_STATIC_DRAW',
            'GL_STATIC_READ', 'GL_STATIC_COPY', 'GL_DYNAMIC_DRAW',
            'GL_DYNAMIC_READ', or 'GL_DYNAMIC_COPY'.
            Infos: http://www.opengl.org/sdk/docs/man/xhtml/glBufferData.xml
        `target`: string, default to 'GL_ARRAY_BUFFER'
            Target of the VBO. Can be one of 'GL_ARRAY_BUFFER',
            'GL_ELEMENT_ARRAY_BUFFER', 'GL_PIXEL_PACK_BUFFER', or
            'GL_PIXEL_UNPACK_BUFFER'.
            Infos: http://www.opengl.org/sdk/docs/man/xhtml/glBufferData.xml
    '''

    __slots__ = ('_vbo', '_vbo_usage', '_vbo_target',
                 '_data', '_format', '_type', '_count')

    def __init__(self, **kwargs):
        kwargs.setdefault('format', None)
        kwargs.setdefault('type', None)
        kwargs.setdefault('usage', 'GL_DYNAMIC_DRAW')
        kwargs.setdefault('target', 'GL_ARRAY_BUFFER')

        assert(kwargs.get('format') != None)
        assert(kwargs.get('type') != None)

        super(GraphicElement, self).__init__()

        self._data = {}
        self._vbo = {}
        self._vbo_usage = kwargs.get('usage')
        self._vbo_target = kwargs.get('target')
        self._format = {}
        self._type = 0
        self._count = 0
        self.type = kwargs.get('type')
        self.format = kwargs.get('format')

    def __del__(self):
        if hasattr(self, '_vbo'):
            for vbo in self._vbo.values(): 
                vbo.delete()

    def draw(self):
        format, type = self._format, self._type
        if type is None or len(format) == 0:
            return

        # bind data and enable required client state
        # first, for each format component, extract the gl function to use
        # and bind the vbo associated + activate
        _vbo = self._vbo
        for fmt, size in format.items():
            func, state = _pointers_gl[fmt[0]]
            _vbo[fmt].bind()
            func(size, GL_FLOAT, 0, None)
            glEnableClientState(state)

        # activate at the very last moment all changes done on context
        self.context.flush()

        # draw array
        glDrawArrays(type, 0, self.count)

        # deactivate client state
        for fmt in format.keys():
            _vbo[fmt].unbind()
            glDisableClientState(_pointers_gl[fmt[0]][1])

    def _set_format(self, format):
        if type(format) == str:
            # transform the 'vvttcccc' to
            # {'v': 2, 't': 2, 'c': 4}
            self._format = {}
            f, last = [], None
            for x in format:
                if last is None:
                    last = x
                elif last[0] == x:
                    last += x
                else:
                    self._format[last[0]] = len(last)
                    last = x
            if last is not None:
                self._format[last[0]] = len(last)
        elif type(format) == dict:
            self._format = format
        else:
            raise Exception('Invalid format')
    def _get_format(self):
        return ''.join([x * y for x, y in self._format.items()])
    format = property(_get_format, _set_format,
        doc='Return the format of the graphic in string (eg. "vvttcccc")')

    def _set_data(self, typ, data):
        try:
            _vbo = self._vbo[typ]
        except KeyError:
            _vbo = vbo.VBO('', usage=self._vbo_usage, target=self._vbo_target)
            self._vbo[typ] = _vbo
        if typ == 'v':
            self._count = len(data) / self._format['v']
        if type(data) is not array:
            data = array('f', data)
        self._data[typ] = data
        _vbo.set_array(data.tostring())
    def _get_data(self, typ):
        try:
            return self._data[typ]
        except KeyError:
            return None
    data_v = property(
        lambda self: self._get_data('v'),
        lambda self, x: self._set_data('v', x),
        doc='Get/set the vertex coordinates data')
    data_c = property(
        lambda self: self._get_data('c'),
        lambda self, x: self._set_data('c', x),
        doc='Get/set the colors coordinates data')
    data_t = property(
        lambda self: self._get_data('t'),
        lambda self, x: self._set_data('t', x),
        doc='Get/set the texture coordinates data')
    data_n = property(
        lambda self: self._get_data('n'),
        lambda self, x: self._set_data('n', x),
        doc='Get/set the normal coordinates data')
    data_e = property(
        lambda self: self._get_data('e'),
        lambda self, x: self._set_data('e', x),
        doc='Get/set the edges data (not used yet.)')
    data_i = property(
        lambda self: self._get_data('i'),
        lambda self, x: self._set_data('i', x),
        doc='Get/set the indexes data (not used yet.)')

    def _get_type(self):
        return self._type
    def _set_type(self, x):
        if type(x) is str:
            x = _type_gl[x]
        self._type = x
    type = property(_get_type, _set_type,
        doc='''
            Specify how the graphic will be drawed. One of: 'lines',
            'line_loop', 'line_strip', 'triangles', 'triangle_fan',
            'triangle_strip', 'quads', 'quad_strip', 'points', 'polygon'
        ''')

    @property
    def count(self):
        '''Return the number of elements (if format is vv, and you have 4
        vertex, it will return 2). The number of elements is calculated on
        vertex.'''
        return self._count


class Line(GraphicElement):
    '''
    Construct line from points.

    :Parameters:
        `points`: list
            List of points, in the format [x, y, x, y...]
    '''
    __slots__ = ('points', '_need_build', '_points')
    def __init__(self, points=[], **kwargs):
        kwargs.setdefault('type', 'line_loop')
        super(Line, self).__init__(format='vv', **kwargs)
        self._need_build = True
        self._points = []
        self.points = points

    def build(self):
        self.data_v = self._points

    def draw(self):
        if self._need_build:
            self.build()
            self._need_build = False
        super(Line, self).draw()

    def _get_points(self):
        return self._points
    def _set_points(self, points):
        self._points = points
        self._need_build = True
    points = property(_get_points, _set_points,
        doc='''Add/remove points of the line (list of [x, y, x, y ...])'''
    )

class Point(GraphicElement):
    '''
    Draw multiple points.

    :Parameters:
        `texture`: texture, default to None
            Specify the texture to use for drawing point
        `radius`: float, default to 1.
            Size of the point to draw, in pixel.
        `steps`: int, default to None
            Number of step between 2 points
    '''
    __slots__ = ('_texture', '_radius', '_points', '_stmt', '_need_build',
                 '_steps')
    def __init__(self, points=[], **kwargs):
        kwargs.setdefault('format', 'vv')
        kwargs.setdefault('type', 'points')

        super(Point, self).__init__(**kwargs)

        self._need_build = True
        self._texture = kwargs.get('texture', None)
        self._radius = kwargs.get('radius', 1.)
        self._steps = kwargs.get('steps', None)
        self._points = points
        self._stmt = None
        if self._texture:
            self._stmt = gx_texture(self._texture)

    def build(self):
        outputList = []
        points = self._points

        if len(self._points) % 2 == 1:
            raise Exception('Points list must be a pair length number (not impair)')

        if self.type != 'points':
            # extract 4 points each 2 points
            for i in xrange(0, len(points) - 2, 2):

                # extract our 2 points
                p1x, p1y = (points[i], points[i+1])
                p2x, p2y = (points[i+2], points[i+3])

                # calculate vector and distance
                dx,dy = p2x - p1x, p2y - p1y
                dist = sqrt(dx * dx + dy * dy)

                # determine step
                steps = self._steps
                if steps is None:
                    steps = max(1, int(dist)/4)

                # construct pointList
                pointList = [0, 0] * steps
                fsteps = float(steps)
                for i in xrange(steps):
                    pointList[i * 2]   = p1x + dx* (i / fsteps)
                    pointList[i * 2 + 1] = p1y + dy* (i / fsteps)

                # append to the result
                outputList += pointList

        # set vertex
        self.data_v = outputList

    def draw(self):
        if self._need_build:
            self.build()
            self._need_build = False
        stmt = self._stmt
        if stmt:
            stmt.bind()
            glEnable(GL_POINT_SPRITE_ARB)
            glTexEnvi(GL_POINT_SPRITE_ARB, GL_COORD_REPLACE_ARB, GL_TRUE)
            glPointSize(self._radius)
        super(Point, self).draw()
        if stmt:
            glDisable(GL_POINT_SPRITE_ARB)
            stmt.release()

    def _get_step(self):
        return self._step
    def _set_step(self, step):
        if self._step == step:
            return False
        self._step = step
        self._need_build = True
        return True
    step = property(_get_step, _set_step,
        doc='Object step (integer)')

    def _get_points(self):
        return self._points
    def _set_points(self, points):
        if self._points == points:
            return False
        self._points = points
        self._need_build = True
        return True
    points = property(_get_points, _set_points,
        doc='Object points (list in the format [x, y, x, y...])')

    def _get_radius(self):
        return self._radius
    def _set_radius(self, radius):
        if self._radius == radius:
            return False
        self._radius = radius
        self._need_build = True
        return True
    radius = property(_get_radius, _set_radius,
        doc='Object radius (float)')

    def _get_texture(self):
        return self._texture
    def _set_texture(self, x):
        if self._texture == x:
            return
        self._texture = x
        if self._texture:
            self._stmt = gx_texture(self._texture)
    texture = property(_get_texture, _set_texture,
        doc='Texture to use on the object (Texture)'
    )

    def _set_type(self, x):
        super(Point, self)._set_type(x)
        self._need_build = True
    type = property(GraphicElement._get_type, _set_type)

class Rectangle(GraphicElement):
    '''
    Construct a rectangle from position + size.
    The rectangle can be use to draw shape of rectangle, filled rectangle,
    textured rectangle, rounded rectangle...

    ..warning ::
        Each time you change a property of the rectangle, the vertex list is
        rebuilt automatically at the next draw() call.

    :Parameters:
        `*values`: list, default to None
            Can be used to provide a tuple of (x, y, w, h)
        `pos`: list, default to (0, 0)
            Position of the rectangle
        `size`: list, default to (1, 1)
            Size of the rectangle
        `texture`: texture, default to None
            Specify the texture to use for the rectangle
        `tex_coords`: list, default to None
            If a texture is specified, the tex_coords will be taken from the
            texture argument. Otherwise, it will be set on 0-1 range.
        `colors_coords`: list, default to None
            Can be used to specify a color for each vertex drawed.
    '''
    __slots__ = ('_pos', '_size', '_texture', '_tex_coords', '_colors_coords',
                 '_need_build', '_stmt')
    def __init__(self, *values, **kwargs):
        kwargs.setdefault('type', 'quads')
        kwargs.setdefault('pos', (0, 0))
        kwargs.setdefault('size', (1, 1))
        kwargs.setdefault('texture', None)
        kwargs.setdefault('tex_coords', None)
        kwargs.setdefault('colors_coords', None)

        format = 'vv'
        if kwargs.get('texture'):
            format += 'tt'
        if kwargs.get('colors_coords'):
            format += 'cccc'
        kwargs.setdefault('format', format)

        super(Rectangle, self).__init__(**kwargs)

        self._pos = kwargs.get('pos')
        self._size = kwargs.get('size')
        if len(values) == 4:
            x, y, w, h = values
            self._pos = x, y
            self._size = w, h
        elif len(values) != 0:
            raise Exception('Rectangle values must be passed like this: Rectangle(x, y, w, h)')
        self._texture = kwargs.get('texture')
        self._tex_coords = kwargs.get('tex_coords')
        self._colors_coords = kwargs.get('colors_coords')
        self._need_build = True
        self._stmt = None
        if self._texture:
            self._stmt = gx_texture(self._texture)

    def build(self):
        '''Build all the vbos. This is automaticly called when a property
        change (position, size, tex_coords...)'''
        # build vertex
        x, y = self.pos
        w, h = self.size
        self.data_v = (x, y, x + w, y, x + w, y + h, x, y + h)

        # if texture is provided, use it
        texture = self.texture
        if texture:
            tex_coords = self.tex_coords
            if type(texture) in (Texture, TextureRegion):
                tex_coords = texture.tex_coords
            # if tex_coords is provided, use it
            if tex_coords is None:
                tex_coords = (0.0,0.0, 1.0,0.0, 1.0,1.0, 0.0,1.0)

            # assign tex_coords
            self.data_t = tex_coords

        # assign colors coords
        if self.colors_coords:
            self.data_c = self.colors_coords

    def draw(self):
        if self._need_build:
            self.build()
            self._need_build = False
        stmt = self._stmt
        if stmt:
            stmt.bind()
        super(Rectangle, self).draw()
        if stmt:
            stmt.release()

    def _get_size(self):
        return self._size
    def _set_size(self, size):
        if self._size == size:
            return False
        self._size = size
        self._need_build = True
        return True
    size = property(_get_size, _set_size,
        doc='Object size (width, height)')

    def _get_width(self):
        return self._size[0]
    def _set_width(self, w):
        if self._size[0] == w:
            return False
        self._size = (w, self._size[1])
        self._need_build = True
        return True
    width = property(_get_width, _set_width,
        doc='Object width')

    def _get_height(self):
        return self._size[1]
    def _set_height(self, h):
        if self._size[1] == h:
            return False
        self._size = (self._size[0], h)
        self._need_build = True
        return True
    height = property(_get_height, _set_height,
        doc='Object height')

    def _get_pos(self):
        return self._pos
    def _set_pos(self, pos):
        if pos == self._pos:
            return False
        self._pos = tuple(pos)
        self._need_build = True
        return True
    pos = property(_get_pos, _set_pos,
        doc='Object position (x, y)')

    def _get_x(self):
        return self._pos[0]
    def _set_x(self, x):
        if x == self.pos[0]:
            return False
        self._pos = (x, self.y)
        self._need_build = True
        return True
    x = property(_get_x, _set_x,
        doc = 'Object X position')

    def _get_y(self):
        return self._pos[1]
    def _set_y(self, y):
        if y == self.pos[1]:
            return False
        self._pos = (self.x, y)
        self._need_build = True
        return True
    y = property(_get_y, _set_y,
        doc = 'Object Y position')

    def _get_center(self):
        return (self._pos[0] + self._size[0] / 2., self._pos[1] + self._size[1] / 2.)
    def _set_center(self, center):
        return self._set_pos((center[0] - self._size[0] / 2.,
                              center[1] - self._size[1] / 2.))
    center = property(_get_center, _set_center,
        doc='Object center (cx, cy)')

    def _get_texture(self):
        return self._texture
    def _set_texture(self, x):
        if self._texture == x:
            return
        self._texture = x
        if self._texture:
            self._stmt = gx_texture(self._texture)
    texture = property(_get_texture, _set_texture,
        doc='Texture to use on the object')

    def _get_tex_coords(self):
        return self._tex_coords
    def _set_tex_coords(self, x):
        if self._tex_coords == x:
            return
        self._tex_coords = x
        self._need_build = True
    tex_coords = property(_get_tex_coords, _set_tex_coords,
        doc='''
        Texture coordinates to use on the object. If nothing is set, it
        will take the coordinates from the current texture
        ''')

    def _get_colors_coords(self):
        return self._colors_coords
    def _set_colors_coords(self, x):
        if self._colors_coords == x:
            return
        self._colors_coords = x
        self._need_build = True
    colors_coords = property(_get_colors_coords, _set_colors_coords,
        doc='Colors coordinates for each vertex')

class Text(Rectangle):
    '''Draw a Text/Label.

    Support all the arguments from `getLabel` function.
    '''
    __slots__ = ('_label', '_labelobj', '_kwargs')
    def __init__(self, label, **kwargs):
        kwargs.setdefault('type', 'quads')
        kwargs.setdefault('format', 'vvtt')
        super(Text, self).__init__(**kwargs)
        self._label = ''
        self._labelobj = None
        self._kwargs = kwargs
        self.label = label

    def _get_label(self):
        return self._label
    def _set_label(self, x):
        if self._label == x:
            return
        self._label = x
        self._labelobj = getLabel(self._label, **self._kwargs)
        self.texture = self._labelobj.texture
        self.size = self._labelobj.size
        self._need_build = True
    label = property(_get_label, _set_label,
        doc='Colors coordinates for each vertex')


class RoundedRectangle(Rectangle):
    '''Draw a rounded rectangle

    warning.. ::
        Rounded rectangle support only vertex, not other things right now.
        It may change in the future.

    :Parameters:
        `radius` : int, default to 5
            Radius of corner
        `precision` : float, default to 0.5
            Precision of corner angle
        `corners` : tuple of bool, default to (True, True, True, True)
            Indicate if round must be draw for each corners
            starting to bottom-left, bottom-right, top-right, top-left
    '''
    __slots__ = ('_corners', '_precision', '_radius')
    def __init__(self, *values, **kwargs):
        kwargs.setdefault('type', 'polygon')
        super(RoundedRectangle, self).__init__(**kwargs)
        if len(values) == 4:
            x, y, w, h = values
            self._pos = x, y
            self._size = w, h
        elif len(values) != 0:
            raise Exception('RoundedRectangle values must be passed like this: Rectangle(x, y, w, h)')
        self._corners = kwargs.get('corners', (True, True, True, True))
        self._precision = kwargs.get('precision', .2)
        self._radius = kwargs.get('radius', 5)

    def build(self):
        radius = self._radius
        precision = self._precision
        cbl, cbr, ctr, ctl = self._corners
        x, y = self.pos
        w, h = self.size
        data_v = array('f', [])
        if cbr:
            data_v.extend((x + radius, y))
            data_v.extend((x + w - radius, y))
            t = pi * 1.5
            while t < pi * 2:
                sx = x + w - radius + cos(t) * radius
                sy = y + radius + sin(t) * radius
                data_v.extend((sx, sy))
                t += precision
        else:
            data_v.extend((x + w, y))

        if ctr:
            data_v.extend((x + w, y + radius))
            data_v.extend((x + w, y + h - radius))
            t = 0
            while t < pi * 0.5:
                sx = x + w - radius + cos(t) * radius
                sy = y + h -radius + sin(t) * radius
                data_v.extend((sx, sy))
                t += precision
        else:
            data_v.extend((x + w, y + h))

        if ctl:
            data_v.extend((x + w -radius, y + h))
            data_v.extend((x + radius, y + h))
            t = pi * 0.5
            while t < pi:
                sx = x  + radius + cos(t) * radius
                sy = y + h - radius + sin(t) * radius
                data_v.extend((sx, sy))
                t += precision
        else:
            data_v.extend((x, y + h))

        if cbl:
            data_v.extend((x, y + h - radius))
            data_v.extend((x, y + radius))
            t = pi
            while t < pi * 1.5:
                sx = x + radius + cos(t) * radius
                sy = y + radius + sin(t) * radius
                data_v.extend((sx, sy))
                t += precision
        else:
            data_v.extend((x, y))

        self.data_v = data_v

    def _get_corners(self):
        return self._corners
    def _set_corners(self, x):
        if self._corners == x:
            return
        if type(x) not in (list, tuple):
            raise Exception('Invalid corner type')
        if len(x) != 4:
            raise Exception('Must have 4 boolean inside the corners list')
        self._corners = x
        self._need_build = True
    corners = property(_get_corners, _set_corners,
        doc='Get/set the corners to draw (tuple of 4 bool)')

    def _get_precision(self):
        return self._precision
    def _set_precision(self, x):
        if self._precision == x:
            return
        self._precision = x
        self._need_build = True
    precision = property(_get_precision, _set_precision,
        doc='Get/set the precision of the corner (double)')

    def _get_radius(self):
        return self._radius
    def _set_radius(self, x):
        if self._radius == x:
            return
        self._radius = x
        self._need_build = True
    radius = property(_get_radius, _set_radius,
        doc='Get/set the radius of the corner (double)')


class Circle(GraphicElement):
    '''
    Construct a circle from position and radius.
    The circle can be either filled or not.

    ..warning ::
        Each time you change a property of the circle, the vertex list is
        rebuilt automatically at the next draw() call.

    :Parameters:
        `pos`: list, defaults to (0, 0)
            Position of the circle
        `radius`: int, defaults to 5
            Radius of the circle
        `filled`: list, default to False
            Can be used to specify a color for each vertex drawed.
    '''
    __slots__ = ('_pos', '_radius', '_need_build')
    def __init__(self, **kwargs):
        kwargs.setdefault('type', 'line_loop')
        kwargs.setdefault('format', 'vv')
        self._pos = kwargs.setdefault('pos', (0, 0))
        self._radius = kwargs.setdefault('radius', 5)
        self._need_build = True
        super(Circle, self).__init__(**kwargs)
        f = kwargs.setdefault('filled', False)
        self.type = self._determine_type(f)

    def build(self):
        p = array('f')
        for angle_deg in xrange(361):
            # rad = deg * (pi / 180), where pi/180 = 0.0174...
            angle_rad = angle_deg * 0.017453292519943295
            # Polar coordinates to cartesian space
            x = self.x + self._radius * cos(angle_rad)
            y = self.y + self._radius * sin(angle_rad)
            p.append(x)
            p.append(y)
        self.data_v = p

    def draw(self):
        if self._need_build:
            self.build()
            self._need_build = False
        super(Circle, self).draw()

    def _get_radius(self):
        return self._radius
    def _set_radius(self, r):
        if self._radius == r:
            return False
        self._radius = r
        self._need_build = True
        return True
    radius = property(_get_radius, _set_radius,
        doc='Radius of the circle (double)')

    def _determine_type(self, f):
        return 'polygon' if f else 'line_strip'
    def _get_filled(self):
        return True if self._type == 'polygon' else False
    def _set_filled(self, f):
        t = self._determine_type(f)
        if self.type == t:
            return False
        self.type = t
        self._need_build = True
        return True
    filled = property(_get_filled, _set_filled,
        doc='Indicates whether the circle is filled or not')

    def _get_pos(self):
        return self._pos
    def _set_pos(self, pos):
        if pos == self._pos:
            return False
        self._pos = tuple(pos)
        self._need_build = True
        return True
    pos = property(_get_pos, _set_pos,
        doc='Object position (x, y)')

    def _get_x(self):
        return self._pos[0]
    def _set_x(self, x):
        if x == self.pos[0]:
            return False
        self._pos = (x, self.y)
        self._need_build = True
        return True
    x = property(_get_x, _set_x,
        doc = 'Object X position')

    def _get_y(self):
        return self._pos[1]
    def _set_y(self, y):
        if y == self.pos[1]:
            return False
        self._pos = (self.x, y)
        self._need_build = True
        return True
    y = property(_get_y, _set_y,
        doc = 'Object Y position')


class Color(GraphicInstruction):
    '''Define current color to be used (as float values between 0 and 1) ::

        c = Canvas()
        c.color(1, 0, 0, 1)
        c.rectangle(pos=(50, 50), size=(100, 100))

        c.draw()

    .. Note:
        Blending is activated if alpha value != 1

    :Parameters:
        `*color` : list
            Can have 3 or 4 float value (between 0 and 1)
        `sfactor` : opengl factor, default to GL_SRC_ALPHA
            Default source factor to be used if blending is activated
        `dfactor` : opengl factor, default to GL_ONE_MINUS_SRC_ALPHA
            Default destination factor to be used if blending is activated
        `blend` : boolean, default to None
            Set True if you really want to activate blending, even
            if the alpha color is 1 (mean no blending in theory)
    '''

    __slots__ = ('_blend', '_sfactor', '_dfactor', '_color')

    def __init__(self, *color, **kwargs):
        super(Color, self).__init__()

        self._blend = kwargs.get('blend', None)
        self._sfactor = kwargs.get('sfactor', GL_SRC_ALPHA)
        self._dfactor = kwargs.get('dfactor', GL_ONE_MINUS_SRC_ALPHA)
        self._color = color

    def draw(self):
        force_blend = self._blend == True
        color = self._color
        ctx = self.context
        l = len(color)

        if l == 1:
            color = (color[0], color[0], color[0], 1)
        elif l == 3:
            color = (color[0], color[1], color[2], 1)
        elif l == 4:
            pass
        else:
            raise Exception('Unsupported color format')

        ctx.color = color
        if color[3] == 1 and not force_blend:
            ctx.blend = False
        else:
            ctx.blend = True
            ctx.sfactor = self._sfactor
            ctx.dfactor = self._dfactor

    def _get_color(self):
        return self._color
    def _set_color(self, x):
        if self._color == x:
            return
        self._color = x
    color = property(_get_color, _set_color,
        doc='''Get/Set the color in tuple format (r, g, b, a)''')


class CSSRectangle(GraphicInstruction):
    '''
    Construct a rectangle, that handle lot of CSS attribute.
    A CSSRectangle can also be constructed with direct values like ::

        # classical way
        CSSRectangle(pos=(0, 0), size=(500, 500), style=self.style)

        # alternative way
        CSSRectangle(x, y, w, h, style=self.style)

    :Parameters:
        `style`: dict, default to {}
            CSS style dictionnary. Usually, it's the self.style of a widget.
        `prefix`: str, default to None
            Use all the styles with that prefix first.
        `state`: str, default to None
            Use all the styles with that state first.

    :Styles:
        * alpha-background (color)
        * bg-image (filename)
        * border-radius (float)
        * border-radius-precision (float)
        * border-width (float)
        * draw-alpha-background (bool)
        * draw-background (bool)
        * draw-border (bool)
    '''
    __slots__ = ('_style', '_prefix', '_state', '_objects', '_pos', '_size',
                 '_need_build')
    def __init__(self, *values, **kwargs):
        super(CSSRectangle, self).__init__()

        self._objects = []
        self._style = kwargs.get('style', {})
        self._prefix = kwargs.get('prefix', None)
        self._state = kwargs.get('state', None)
        self._pos = kwargs.get('pos', (0, 0))
        self._size = kwargs.get('size', (1, 1))
        if len(values) == 4:
            x, y, w, h = values
            self._pos = x, y
            self._size = w, h
        elif len(values) != 0:
            raise Exception('CSSRectangle values must be passed like this: CSSRectangle(x, y, w, h)')

        self._need_build = True

    def build(self):
        self._objects = []

        state = self._state
        style = self._style
        prefix = self._prefix
        obj = self._objects

        # get background image.
        # don't add anything else if we just have a background image.
        bg_image = style.get('bg-image-' + str(state))
        if not bg_image:
            bg_image = style.get('bg-image')
        if bg_image:
            obj.append(Rectangle(pos=self._pos, size=self._size))
            return

        # lets use the ones for given state,
        # and ignore the regular ones if the state ones are there
        if state:
            state = '-' + state
            newstyle = {}
            overwrites = []
            for s in style:
                if state in s:
                    overwrite  = s.replace(state, '')
                    newstyle[overwrite] = style[s]
                    overwrites.append(overwrite)
                if s not in overwrites:
                    newstyle[s] = style[s]
            style = newstyle

        # hack to remove prefix in style
        if prefix is not None:
            prefix += '-'
            newstyle = {}
            for k in style:
                newstyle[k] = style[k]
            for k in style:
                if prefix in k:
                    newstyle[k.replace(prefix, '')] = style[k]
            style = newstyle

        k = { 'pos': self._pos, 'size': self._size }

        linewidth = style.get('border-width', 1.5)
        bordercolor = None
        if 'border-color' in style:
            bordercolor = style['border-color']

        roundrect = False
        border_radius = style.get('border-radius', 0)
        if border_radius > 0:
            roundrect = True
            k.update({
                'radius': border_radius,
                'precision': style.get('border-radius-precision', .1)
            })

        # set the color of object
        if 'bg-color' in style:
            obj.append(Color(*style['bg-color']))

        # add background object
        if style.get('draw-background', 1):
            if roundrect:
                obj.append(RoundedRectangle(**k))
            else:
                obj.append(Rectangle(**k))

        # add border object
        if style.get('draw-border', 0):
            if linewidth or bordercolor:
                obj.append(GraphicContextSave())
            if linewidth:
                obj.append(GraphicContextChange(linewidth=linewidth))
            if bordercolor:
                obj.append(Color(*bordercolor))
            if roundrect:
                obj.append(RoundedRectangle(type='line_loop', **k))
            else:
                obj.append(Rectangle(type='line_loop', **k))
            if linewidth or bordercolor:
                obj.append(GraphicContextRestore())
            # FIXME
            #if style.get('draw-alpha-background', 0):
            #    drawRoundedRectangleAlpha(alpha=style.get('alpha-background',
            #    (1, 1, .5, .5)], **k)

    def draw(self):
        if self._need_build:
            self.build()
            self._need_build = False
        for x in self._objects:
            x.draw()

    def _get_size(self):
        return self._size
    def _set_size(self, size):
        if self._size == size:
            return False
        self._size = size
        self._need_build = True
        return True
    size = property(_get_size, _set_size,
        doc='Object size (width, height)')

    def _get_width(self):
        return self._size[0]
    def _set_width(self, w):
        if self._size[0] == w:
            return False
        self._size = (w, self._size[1])
        self._need_build = True
        return True
    width = property(_get_width, _set_width,
        doc='Object width')

    def _get_height(self):
        return self._size[1]
    def _set_height(self, h):
        if self._size[1] == h:
            return False
        self._size = (self._size[0], h)
        self._need_build = True
        return True
    height = property(_get_height, _set_height,
        doc='Object height')

    def _get_pos(self):
        return self._pos
    def _set_pos(self, pos):
        if pos == self._pos:
            return False
        self._pos = tuple(pos)
        self._need_build = True
        return True
    pos = property(_get_pos, _set_pos,
        doc='Object position (x, y)')

    def _get_x(self):
        return self._pos[0]
    def _set_x(self, x):
        if x == self.pos[0]:
            return False
        self._pos = (x, self.y)
        self._need_build = True
        return True
    x = property(_get_x, _set_x,
        doc = 'Object X position')

    def _get_y(self):
        return self._pos[1]
    def _set_y(self, y):
        if y == self.pos[1]:
            return False
        self._pos = (self.x, y)
        self._need_build = True
        return True
    y = property(_get_y, _set_y,
        doc = 'Object Y position')

    def _get_center(self):
        return (self._pos[0] + self._size[0] / 2., self._pos[1] + self._size[1] / 2.)
    def _set_center(self, center):
        return self._set_pos((center[0] - self._size[0] / 2.,
                              center[1] - self._size[1] / 2.))
    center = property(_get_center, _set_center,
        doc='Object center (cx, cy)')

    def _get_state(self):
        return self._state
    def _set_state(self, x):
        if self._state == x:
            return
        self._state = x
        self._need_build = True
    state = property(_get_state, _set_state,
        doc='Get/Set the css state to use')

    def _get_prefix(self):
        return self._prefix
    def _set_prefix(self, x):
        if self._prefix == x:
            return
        self._prefix = x
        self._need_build = True
    prefix = property(_get_prefix, _set_prefix,
        doc='Get/Set the css prefix to use')

    def _get_style(self):
        return self._style
    def _set_style(self, x):
        if self._style == x:
            return
        self._style = x
        self._need_build = True
    style = property(_get_style, _set_style,
        doc='Get/Set the css style to use (normally, its the widget.style property)')


class Canvas(object):
    '''Create a batch of graphic object.
    Can be use to store many graphic instruction, and call them for drawing.
    In a future, we'll do optimization on this, like merge vbo if possible.
    '''

    __slots__ = ('_batch', '_context')

    def __init__(self, **kwargs):
        self._batch = []
        self._context = default_context

    def add(self, graphic):
        '''Add a graphic element to draw'''
        #if isinstance(graphic, GraphicInstruction):
        #    raise Exception('Canvas accept only Graphic Instruction')
        self._batch.append(graphic)
        graphic.context = self._context
        return graphic

    def remove(self, graphic):
        '''Remove a graphic element from the list of objects'''
        try:
            self._batch.remove(graphic)
        except:
            pass

    def clear(self):
        '''Clear all the elements in canvas'''
        self._batch = []

    def draw(self):
        '''Draw all the canvas elements'''
        for x in self._batch:
            x.draw()

    def save(self):
        '''Push the current context to the stack'''
        self.add(GraphicContextSave())

    def restore(self):
        '''Restore the previous saved context'''
        self.add(GraphicContextRestore())

    @property
    def objects(self):
        return self._batch

    # facilities to create object
    def line(self, *largs, **kwargs):
        '''Create a Line() object, and add to the list.
        Check Line() for more information.'''
        return self.add(Line(*largs, **kwargs))

    def point(self, *largs, **kwargs):
        '''Create a Point() object, and add to the list.
        Check Point() for more information.'''
        return self.add(Point(*largs, **kwargs))

    def rectangle(self, *largs, **kwargs):
        '''Create a Rectangle() object, and add to the list.
        Check Rectangle() for more information.'''
        return self.add(Rectangle(*largs, **kwargs))

    def roundedRectangle(self, *largs, **kwargs):
        '''Create a RoundedRectangle() object, and add to the list.
        Check RoundedRectangle() for more information.'''
        return self.add(RoundedRectangle(*largs, **kwargs))

    def cssRectangle(self, *largs, **kwargs):
        '''Create a CSSRectangle() object, and add to the list.
        Check CSSRectangle() for more information.'''
        return self.add(CSSRectangle(*largs, **kwargs))

    def color(self, *largs, **kwargs):
        '''Create a Color() object, and add to the list.
        Check Color() for more information.'''
        return self.add(Color(*largs, **kwargs))

    def text(self, *largs, **kwargs):
        '''Create a Text() object, and add to the list.
        Check Text() for more information.'''
        return self.add(Text(*largs, **kwargs))
