'''
Graphics: Lower level functions to draw in OpenGL.

Our previous graphx package relied on OpenGL's so-called immediate mode.
This mode is no longer allowed in OpenGL 3.0 and OpenGL ES.
This graphics module is the new and stable way to draw all OpenGL elements
in PyMT.
We seriously recommend you use these classes (the old graphx package will be deprecated)!


User mode
---------

For every object you want do draw on the screen, you must create them on a canvas
before drawing. The canvas object is a class that will store
all your graphics elements and draw them efficiently.
This method allows for internal optimizations.
Use it like this ::

    >>> canvas = Canvas()
    >>> canvas.color(1, 0, 0, 1)
    >>> canvas.line([50, 50, 100, 100])

Then, to draw the canvas ::

    >>> canvas.draw()

You can also get a handle for any element of the canvas to change it later ::

    >>> myline = canvas.line([50, 50, 100, 100])
    >>> myline.points += [0, 150]


Expert mode
-----------

You can create your own graphical object.
However, you should still use the canvas object.

An example with a line ::

    # in init function
    >>> line = Line([50, 50, 100, 100])

    # in draw function
    >>> line.draw()

    # If you want to change the points of the line, you can do
    >>> line.points = [80, 80, 100, 100]

    # Or even add points to the line
    >>> line.points += [58, 35]


An example with a rectangle ::

    # in init function
    >>> rect = Rectangle(pos=(50, 50), size=(200, 200))

    # in draw function
    >>> rect.draw()

    # You can change pos, size...
    >>> rect.pos = (10, 10)
    >>> rect.size = (999, 999)

An example with a rectangle and a texture ::

    # in init function
    >>> img = Image('test.png')
    >>> rect = Rectangle(size=(100, 100), texture=img.texture)

    # in draw function
    >>> rect.draw()

'''

#
# Some Cython ressources
# http://docs.cython.org/src/tutorial/cdef_classes.html
#
# TODO
# 1. use our own VBO
# 2. handle ourself texture
# 3. handle all in a shader (aka opengl es)
#


from pymt.baseobject import BaseObject
from pymt.texture import Texture, TextureRegion
from pymt.graphx import getLabel, gx_texture
from pymt.resources import resource_find
from pymt.core.image import Image
from array import array
from OpenGL.arrays import vbo

from c_opengl cimport *

cdef extern from "math.h":
    double cos(double)
    double sin(double)
    double sqrt(double)
#
# Documentation:
#  http://www.openorg/wiki/Vertex_Buffer_Object
#
# Format:
#  v = Vertex (vv = xy, vvv = xyz)
#  c = Color (ccc = rgb, cccc = rgba)
#  t = Texture (tt = uv, ttt = uvw)
#  n = Normal (nn = xy, nnn = xyz)
#  i = Index (color index)
#  e = Edge
#

cdef double pi = 3.1415926535897931
cdef dict texture_map = {}
cdef texture_lookup(filename):
    texture = texture_map.get(filename, None)
    if not texture:
        correctFilename = resource_find(filename)
        if correctFilename is None:
            raise Exception('Unable to found image %s' % filename)
        texture = Image(correctFilename).texture
        print filename, 'texture=', texture
        texture_map[filename] = texture
    return texture

cdef int gl_type_from_str(str typ):
    if typ == 'points':
        return GL_POINTS
    elif typ == 'lines':
        return GL_LINES
    elif typ == 'line_strip':
        return GL_LINE_STRIP
    elif typ == 'line_loop':
        return GL_LINE_LOOP
    elif typ == 'triangles':
        return GL_TRIANGLES
    elif typ == 'triangle_fan':
        return GL_TRIANGLE_FAN
    elif typ == 'triangle_strip':
        return GL_TRIANGLE_STRIP
    elif typ == 'quads':
        return GL_QUADS
    elif typ == 'quad_strip':
        return GL_QUAD_STRIP
    elif typ == 'polygon':
        return GL_POLYGON

cdef class GraphicContext:
    '''Handle the saving/restore of the context

    TODO: explain more how it works
    '''
    cdef dict state
    cdef list stack
    cdef set journal
    cdef readonly int need_flush

    def __cinit__(self):
        self.state = {}
        self.stack = []
        self.journal = set()
        self.need_flush = 0

    def __init__(self):
        # create initial state
        self.reset()
        self.save()

    cpdef set(self, str key, value):
        self.state[key] = value
        self.journal.add(key)
        self.need_flush = 1

    cpdef get(self, str key):
        return self.state[key]

    cpdef reset(self):
        self.set('color', (1, 1, 1, 1))
        self.set('blend', 0)
        self.set('blend_sfactor', GL_SRC_ALPHA)
        self.set('blend_dfactor', GL_ONE_MINUS_SRC_ALPHA)
        self.set('linewidth', 1)

    cpdef save(self):
        self.stack.append(self.state.copy())

    cpdef restore(self):
        newstate = self.stack.pop()
        state = self.state
        for k, v in newstate.iteritems():
            if state[k] != v:
                self.set(k, v)

    cpdef flush(self):
        # activate all the last changes done on context
        # apply all the actions in the journal !
        cdef dict state
        cdef set journal
        cdef str x

        if not self.journal:
            return

        state = self.state
        journal = self.journal
        for x in journal:
            value = state[x]
            if x == 'color':
                glColor4f(value[0], value[1], value[2], value[3])
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
        self.need_flush = 0


#: Default canvas used in graphic element
default_context = GraphicContext()

cdef class GraphicInstruction:
    cdef public GraphicContext context
    def __cinit__(self):
        self.context = default_context
    cpdef draw(self):
        '''Draw/Execute the graphical element on screen'''

cdef class GraphicContextSave(GraphicInstruction):
    cpdef draw(self):
        self.context.save()

cdef class GraphicContextRestore(GraphicInstruction):
    cpdef draw(self):
        self.context.restore()

cdef class GraphicContextChange(GraphicInstruction):
    cdef dict instructions
    def __init__(self, **kwargs):
        GraphicInstruction.__init__(self)
        self.instructions = kwargs
    cpdef draw(self):
        cdef str k
        for k, v in self.instructions.iteritems():
            self.context.set(k, v)

cdef class GraphicElement(GraphicInstruction):
    '''
    This is the lowest graphical element you can use. It's an abstraction to
    Vertex Buffer Object, and you can push your vertex, color, texture ... and
    draw them easily.

    The format of the buffer is specified in character code. For example,
    'vvcccc' means that you'll have 2 vertex + 4 colors coordinates.
    You have 6 differents components that you can use:
        * v: vertex
        * c: color
        * t: texture
        * n: normal
        * i: index (not yet used)
        * e: edge (not yet used)

    For each component, VBOs are separated.

    :Parameters:
        `format`: string, default to None
            The format must be specified at start, and cannot be changed once
            the graphic is created.
        `type`: string, default to None
            Specify how the graphic will be drawn. One of: 'lines',
            'line_loop', 'line_strip', 'triangles', 'triangle_fan',
            'triangle_strip', 'quads', 'quad_strip', 'points', 'polygon'
        `usage`: string, default to 'GL_DYNAMIC_DRAW'
            Specify the usage of VBO. Can be one of 'GL_STREAM_DRAW',
            'GL_STREAM_READ', 'GL_STREAM_COPY', 'GL_STATIC_DRAW',
            'GL_STATIC_READ', 'GL_STATIC_COPY', 'GL_DYNAMIC_DRAW',
            'GL_DYNAMIC_READ', or 'GL_DYNAMIC_COPY'.
            Infos: http://www.openorg/sdk/docs/man/xhtml/glBufferData.xml
        `target`: string, default to 'GL_ARRAY_BUFFER'
            Target of the VBO. Can be one of 'GL_ARRAY_BUFFER',
            'GL_ELEMENT_ARRAY_BUFFER', 'GL_PIXEL_PACK_BUFFER', or
            'GL_PIXEL_UNPACK_BUFFER'.
            Infos: http://www.openorg/sdk/docs/man/xhtml/glBufferData.xml
    '''

    cdef str _vbo_usage
    cdef str _vbo_target
    cdef str _format_str
    cdef int _type, _indices_count
    cdef bytes _indices
    cdef readonly int count

    # declare all possible vbo
    cdef object _vbo_v, _vbo_c, _vbo_t, _vbo_n, _vbo_e, _vbo_i
    cdef object _data_v, _data_c, _data_t, _data_n, _data_e, _data_i
    cdef int _size_v, _size_c, _size_t
    cdef int _use_v, _use_c, _use_t, _use_n, _use_e, _use_i, _use_indices

    def __cinit__(self):
        self.count = 0
        self._format_str = ''
        self._type = GL_POINTS
        self._vbo_usage = 'GL_DYNAMIC_DRAW'
        self._vbo_target = 'GL_ARRAY_BUFFER'
        self._use_v = 0
        self._use_c = 0
        self._use_t = 0
        self._use_n = 0
        self._use_e = 0
        self._use_i = 0
        self._use_indices = 0
        self._vbo_v = None
        self._vbo_c = None
        self._vbo_t = None
        self._vbo_n = None
        self._vbo_e = None
        self._vbo_i = None
        self._indices = ''
        self._indices_count = 0

    def __init__(self, **kwargs):
        kwargs.setdefault('format', None)
        kwargs.setdefault('type', None)

        assert(kwargs.get('format') != None)
        assert(kwargs.get('type') != None)

        GraphicInstruction.__init__(self)

        self._vbo_usage = kwargs.get('usage', 'GL_DYNAMIC_DRAW')
        self._vbo_target = kwargs.get('target', 'GL_ARRAY_BUFFER')
        self.type = kwargs.get('type')
        self.format = kwargs.get('format')

    def __del__(self):
        if hasattr(self, '_vbo'):
            for vbo in self._vbo.itervalues():
                vbo.delete()

    cpdef draw(self):
        if self._use_v:
            self._vbo_v.bind()
            glVertexPointer(self._size_v, GL_FLOAT, 0, NULL)
            glEnableClientState(GL_VERTEX_ARRAY)
        if self._use_c:
            self._vbo_c.bind()
            glColorPointer(self._size_c, GL_FLOAT, 0, NULL)
            glEnableClientState(GL_COLOR_ARRAY)
        if self._use_t:
            self._vbo_t.bind()
            glTexCoordPointer(self._size_t, GL_FLOAT, 0, NULL)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        if self._use_n:
            self._vbo_n.bind()
            glNormalPointer(GL_FLOAT, 0, NULL)
            glEnableClientState(GL_NORMAL_ARRAY)
        if self._use_e:
            self._vbo_e.bind()
            glEdgeFlagPointer(0, NULL)
            glEnableClientState(GL_EDGE_FLAG_ARRAY)
        if self._use_i:
            self._vbo_i.bind()
            glIndexPointer(GL_FLOAT, 0, NULL)
            glEnableClientState(GL_INDEX_ARRAY)

        # activate at the very last moment all changes done on context
        if self.context.need_flush:
            self.context.flush()

        # draw array
        if self._use_indices:
            glDrawElements(self._type, self._indices_count, GL_UNSIGNED_INT, <char *>self._indices)
        else:
            glDrawArrays(self._type, 0, self.count)

        # unbind all
        if self._use_v:
            self._vbo_v.unbind()
            glDisableClientState(GL_VERTEX_ARRAY)
        if self._use_c:
            self._vbo_c.unbind()
            glDisableClientState(GL_COLOR_ARRAY)
        if self._use_t:
            self._vbo_t.unbind()
            glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        if self._use_n:
            self._vbo_n.unbind()
            glDisableClientState(GL_NORMAL_ARRAY)
        if self._use_e:
            self._vbo_e.unbind()
            glDisableClientState(GL_EDGE_FLAG_ARRAY)
        if self._use_i:
            self._vbo_i.unbind()
            glDisableClientState(GL_INDEX_ARRAY)

    cdef _reset_format(self):
        self._use_v = 0
        self._use_c = 0
        self._use_t = 0
        self._use_n = 0
        self._use_e = 0
        self._use_i = 0

    cdef _activate_format(self, str fmt, int size):
        if fmt == 'v':
            self._use_v = 1
            self._size_v = size
        elif fmt == 'c':
            self._use_c = 1
            self._size_c = size
        elif fmt == 't':
            self._use_t = 1
            self._size_t = size
        elif fmt == 'n':
            self._use_n = 1
        elif fmt == 'e':
            self._use_e = 1
        elif fmt == 'i':
            self._use_i = 1

    property format:
        '''Return the format of the graphic in string (eg. "vvttcccc")'''
        def __set__(self, str fmt):
            # transform the 'vvttcccc' to
            cdef str last, x
            last = ''
            self._reset_format()
            for x in fmt:
                if not last:
                    last = x
                elif last[0] == x:
                    last += x
                else:
                    self._activate_format(last[0], len(last))
                    last = x
            if last:
                self._activate_format(last[0], len(last))
            self._format_str = ''
            if self._use_v: self._format_str += 'v' * self._size_v
            if self._use_c: self._format_str += 'c' * self._size_c
            if self._use_t: self._format_str += 't' * self._size_t
            if self._use_n: self._format_str += 'n'
            if self._use_e: self._format_str += 'e'
            if self._use_i: self._format_str += 'i'
        def __get__(self):
            return self._format_str

    cdef _set_data(self, vbo, data):
        if vbo == self._vbo_v:
            self.count = len(data) / self._size_v
        if type(data) is not array:
            data = array('f', data)
        #self._data[typ] = data
        vbo.set_array(data.tostring())

    def _get_data_v(self): return self._data_v
    def _get_data_c(self): return self._data_c
    def _get_data_t(self): return self._data_t
    def _get_data_n(self): return self._data_n
    def _get_data_e(self): return self._data_e
    def _get_data_i(self): return self._data_i

    cdef object _create_vbo(self):
        return vbo.VBO('', usage=self._vbo_usage, target=self._vbo_target)

    def _set_data_v(self, x):
        if not self._vbo_v: self._vbo_v = self._create_vbo()
        return self._set_data(self._vbo_v, x)
    def _set_data_c(self, x):
        if not self._vbo_c: self._vbo_c = self._create_vbo()
        return self._set_data(self._vbo_c, x)
    def _set_data_t(self, x):
        if not self._vbo_t: self._vbo_t = self._create_vbo()
        return self._set_data(self._vbo_t, x)
    def _set_data_n(self, x):
        if not self._vbo_n: self._vbo_n = self._create_vbo()
        return self._set_data(self._vbo_n, x)
    def _set_data_e(self, x):
        if not self._vbo_e: self._vbo_e = self._create_vbo()
        return self._set_data(self._vbo_e, x)
    def _set_data_i(self, x):
        if not self._vbo_i: self._vbo_i = self._create_vbo()
        return self._set_data(self._vbo_i, x)
    data_v = property(_get_data_v, _set_data_v,
        doc='Get/set the vertex coordinates data')
    data_c = property(_get_data_c, _set_data_c,
        doc='Get/set the colors coordinates data')
    data_t = property(_get_data_t, _set_data_t,
        doc='Get/set the texture coordinates data')
    data_n = property(_get_data_n, _set_data_n,
        doc='Get/set the normal coordinates data')
    data_e = property(_get_data_e, _set_data_e,
        doc='Get/set the edges data (not used yet.)')
    data_i = property(_get_data_i, _set_data_i,
        doc='Get/set the indexes data (not used yet.)')

    def _get_indices(self):
        return self._indices
    def _set_indices(self, x):
        if x is None:
            self._use_indices = 0
            return
        self._indices = array('I', x).tostring()
        self._indices_count = len(x)
        self._use_indices = 1
    indices = property(_get_indices, _set_indices,
        doc='(optional) Use an indice array to draw')

    def _get_type(self):
        return self._type
    def _set_type(self, x):
        if type(x) is str:
            x = gl_type_from_str(x)
        self._type = x
    type = property(_get_type, _set_type,
        doc='''
            Specify how the graphic will be drawed. One of: 'lines',
            'line_loop', 'line_strip', 'triangles', 'triangle_fan',
            'triangle_strip', 'quads', 'quad_strip', 'points', 'polygon'
        ''')


cdef class Line(GraphicElement):
    '''
    Construct line from points.

    :Parameters:
        `points`: list
            List of points, in the format [x, y, x, y...]
    '''
    cdef list _points
    cdef int _need_build

    def __init__(self, points=[], **kwargs):
        kwargs.setdefault('format', 'vv')
        kwargs.setdefault('type', 'line_strip')
        GraphicElement.__init__(self, **kwargs)
        self._need_build = 1
        self._points = []
        self.points = points

    cpdef build(self):
        self.data_v = self._points

    cpdef draw(self):
        if self._need_build:
            self.build()
            self._need_build = 0
        GraphicElement.draw(self)

    def _get_points(self):
        return self._points
    def _set_points(self, points):
        self._points = list(points)
        self._need_build = 1
    points = property(_get_points, _set_points,
        doc='''Add/remove points of the line (list of [x, y, x, y ...])'''
    )

cdef class Point(GraphicElement):
    '''
    Draw multiple points.

    :Parameters:
        `texture`: texture, default to None
            Specify the texture to use to draw the points
        `radius`: float, default to 1.
            Size of the point to draw, in pixel.
        `steps`: int, default to None
            Number of steps between 2 points
    '''
    cdef object _texture
    cdef double _radius
    cdef list _points
    cdef object _stmt
    cdef int _use_stmt
    cdef int _need_build
    cdef int _steps

    def __cinit__(self):
        self._points = []
        self._use_stmt = 0
        self._need_build = 1
        self._use_stmt = 0
        self._stmt = None

    def __init__(self, points=[], **kwargs):
        kwargs.setdefault('format', 'vv')
        kwargs.setdefault('type', 'points')

        GraphicElement.__init__(self, **kwargs)

        self._texture = kwargs.get('texture', None)
        self._radius = kwargs.get('radius', 1.)
        self._steps = kwargs.get('steps', -1)
        self.points = points
        if self._texture:
            self._stmt = gx_texture(self._texture)
            self._use_stmt = 1

    cpdef build(self):
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
                if steps < 0:
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

    cpdef draw(self):
        if self._need_build:
            self.build()
            self._need_build = 0
        if self._use_stmt:
            stmt = self._stmt
            stmt.bind()
            glEnable(0x8861) # GL_POINT_SPRITE_ARB
            glTexEnvi(0x8861, 0x8862, GL_TRUE) # GL_COORD_REPLACE_ARB
            glPointSize(self._radius)
            GraphicElement.draw(self)
            glDisable(0x8861)
            stmt.release()
        else:
            GraphicElement.draw(self)

    def _get_step(self):
        return self._step
    def _set_step(self, step):
        if self._step == step:
            return False
        self._step = step
        self._need_build = 1
        return True
    step = property(_get_step, _set_step,
        doc='Object step (integer)')

    def _get_points(self):
        return self._points
    def _set_points(self, points):
        self._points = list(points)
        self._need_build = 1
    points = property(_get_points, _set_points,
        doc='Object points (list in the format [x, y, x, y...])')

    def _get_radius(self):
        return self._radius
    def _set_radius(self, radius):
        if self._radius == radius:
            return False
        self._radius = radius
        self._need_build = 1
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
        GraphicElement._set_type(self, x)
        self._need_build = 1
    type = property(GraphicElement._get_type, _set_type)

cdef class Rectangle(GraphicElement):
    '''
    Construct a rectangle from position and size.
    This can be use to draw the shape of a rectangle, a filled rectangle,
    a textured rectangle, a rounded rectangle...

    .. warning::
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
            Can be used to specify a color for each vertex drawn.
    '''
    cdef tuple _pos
    cdef tuple _size
    cdef object _texture
    cdef list _tex_coords
    cdef list _colors_coords
    cdef int _need_build
    cdef object _stmt
    cdef int _use_stmt

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

        GraphicElement.__init__(self, **kwargs)

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
        self._need_build = 1
        self._use_stmt = 0
        self._stmt = None
        if self._texture:
            self._stmt = gx_texture(self._texture)
            self._use_stmt = 1

    cpdef build(self):
        '''Build all the vbos. This is automaticly called when a property
        changes (position, size, tex_coords...)'''
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

    cpdef draw(self):
        if self._need_build:
            self.build()
            self._need_build = 0
        if self._use_stmt:
            stmt = self._stmt
            stmt.bind()
            GraphicElement.draw(self)
            stmt.release()
        else:
            GraphicElement.draw(self)

    def _get_size(self):
        return self._size
    def _set_size(self, size):
        if self._size == size:
            return False
        self._size = size
        self._need_build = 1
        return True
    size = property(_get_size, _set_size,
        doc='Object size (width, height)')

    def _get_width(self):
        return self._size[0]
    def _set_width(self, w):
        if self._size[0] == w:
            return False
        self._size = (w, self._size[1])
        self._need_build = 1
        return True
    width = property(_get_width, _set_width,
        doc='Object width')

    def _get_height(self):
        return self._size[1]
    def _set_height(self, h):
        if self._size[1] == h:
            return False
        self._size = (self._size[0], h)
        self._need_build = 1
        return True
    height = property(_get_height, _set_height,
        doc='Object height')

    def _get_pos(self):
        return self._pos
    def _set_pos(self, pos):
        if pos == self._pos:
            return False
        self._pos = tuple(pos)
        self._need_build = 1
        return True
    pos = property(_get_pos, _set_pos,
        doc='Object position (x, y)')

    def _get_x(self):
        return self._pos[0]
    def _set_x(self, x):
        if x == self.pos[0]:
            return False
        self._pos = (x, self.y)
        self._need_build = 1
        return True
    x = property(_get_x, _set_x,
        doc = 'Object X position')

    def _get_y(self):
        return self._pos[1]
    def _set_y(self, y):
        if y == self.pos[1]:
            return False
        self._pos = (self.x, y)
        self._need_build = 1
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
        self._need_build = 1
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
        self._need_build = 1
    colors_coords = property(_get_colors_coords, _set_colors_coords,
        doc='Colors coordinates for each vertex')

cdef class ImageRectangle(Rectangle):
    ''' Draw an Image rectangle, similar to border-image in CSS3.
    '''
    cdef list _borders
    cdef object _mode

    def __init__(self, *largs, **kwargs):
        kwargs.setdefault('type', 'quads')
        kwargs.setdefault('format', 'vvtt')
        Rectangle.__init__(self, *largs, **kwargs)
        self._borders = self.convert_border(kwargs.get('borders', [0]))
        self._mode = 'strech'
        self.indices = [
            0, 4, 5, 1,
            1, 2, 6, 5,
            2, 3, 7, 6,
            4, 5, 9, 8,
            5, 6, 10, 9,
            6, 7, 11, 10,
            8, 9, 13, 12,
            9, 10, 14, 13,
            10, 11, 15, 14
        ]

    cpdef build(self):
        cdef double w, h, x, y, tw, th, l1, l2, l3, l4
        cdef list cpos, ctex
        cdef int idx

        texture = self._texture
        mode = self._mode
        w, h = self._size
        x, y = self._pos
        l1, l2, l3, l4 = self._borders

        # take the texture size from the tex_coords
        tw = float(texture.tex_coords[2])
        th = float(texture.tex_coords[5])

        # calculate texture coordinate
        texcoords = texture.tex_coords
        if self._mode == 'strech':
            ctex = [
                0,          th,
                l4,         th,
                tw - l2,    th,
                tw,         th,

                0,          th - l1,
                l4,         th - l1,
                tw - l2,    th - l1,
                tw,         th - l1,

                0,          l3,
                l4,         l3,
                tw - l2,    l3,
                tw,         l3,

                0,          0,
                l4,         0,
                tw - l2,    0,
                tw,         0,
            ]

            cpos = [
                0,          h,
                l4,         h,
                w - l2,     h,
                w,          h,

                0,          h - l1,
                l4,         h - l1,
                w - l2,     h - l1,
                w,          h - l1,

                0,          l3,
                l4,         l3,
                w - l2,     l3,
                w,          l3,

                0,          0,
                l4,         0,
                w - l2,     0,
                w,          0,

            ]

        # move to position
        for idx in xrange(len(cpos)):
            if idx % 2 == 0:
                cpos[idx] += x
            else:
                cpos[idx] += y

        # construct the vbo
        self.data_v = cpos
        self.data_t = ctex

    def convert_border(self, largs):
        if len(largs) == 0:
            l1 = l2 = l3 = l4 = 0
        elif len(largs) == 1:
            l1 = l2 = l3 = l4 = largs[0]
        elif len(largs) == 2:
            l1 = l3 = largs[0]
            l2 = l4 = largs[1]
        elif len(largs) == 4:
            l1, l2, l3, l4 = largs
        else:
            assert('Unknown directive')
        return [l1, l2, l3, l4]

    def _get_borders(self):
        return self._borders
    def _set_borders(self, x):
        x = self.convert_border(x)
        if x == self._borders:
            return
        self._borders = x
        self._need_build = 1
    borders = property(_get_borders, _set_borders,
        doc='Borders in pixels of the image')

    def _get_mode(self):
        return self._mode
    def _set_mode(self, x):
        if self._mode == x:
            return
        self._mode = x
        assert(self._mode in ('strech', ))
        self._need_build = 1
    mode = property(_get_mode, _set_mode,
        doc='Mode of the drawing (only strech is supported')


cdef class Text(Rectangle):
    '''Draw a Text/Label.

    Supports all the arguments from the `getLabel` function.
    '''
    # XXX ^--- and which exactly?
    cdef str _label
    cdef object _labelobj
    cdef dict _kwargs

    def __init__(self, label, **kwargs):
        kwargs.setdefault('type', 'quads')
        kwargs.setdefault('format', 'vvtt')
        Rectangle.__init__(self, **kwargs)
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
        self._need_build = 1
    label = property(_get_label, _set_label,
        doc='Colors coordinates for each vertex')


cdef class RoundedRectangle(Rectangle):
    '''Draw a rounded rectangle

    .. warning::
        Rounded rectangle supports only vertex, not other things right now.
        It may change in the future.

    :Parameters:
        `radius` : int, default to 5
            Radius of the corners
        `precision` : float, default to 0.5
            Precision of corner angle
        `corners` : tuple of bool, default to (True, True, True, True)
            Indicate which corners are to be rounded.
            Bools in the order: bottom-left, bottom-right, top-right, top-left
    '''
    cdef tuple _corners
    cdef double _precision
    cdef double _radius

    def __init__(self, *values, **kwargs):
        kwargs.setdefault('type', 'polygon')
        Rectangle.__init__(self, **kwargs)
        if len(values) == 4:
            x, y, w, h = values
            self._pos = x, y
            self._size = w, h
        elif len(values) != 0:
            raise Exception('RoundedRectangle values must be passed like this: Rectangle(x, y, w, h)')
        self._corners = kwargs.get('corners', (True, True, True, True))
        self._precision = kwargs.get('precision', .2)
        self._radius = kwargs.get('radius', 5)

    cpdef build(self):
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
            raise Exception('Must have 4 bool inside the corners list')
        self._corners = x
        self._need_build = 1
    corners = property(_get_corners, _set_corners,
        doc='Get/set the corners to draw (tuple of 4 bool)')

    def _get_precision(self):
        return self._precision
    def _set_precision(self, x):
        if self._precision == x:
            return
        self._precision = x
        self._need_build = 1
    precision = property(_get_precision, _set_precision,
        doc='Get/set the precision of the corner (double)')

    def _get_radius(self):
        return self._radius
    def _set_radius(self, x):
        if self._radius == x:
            return
        self._radius = x
        self._need_build = 1
    radius = property(_get_radius, _set_radius,
        doc='Get/set the radius of the corner (double)')


cdef class Circle(GraphicElement):
    '''
    Construct a circle from position and radius.
    The circle can be either filled or not.

    .. warning::
        Each time you change a property of the circle, the vertex list is
        rebuilt automatically at the next draw() call.

    :Parameters:
        `pos`: list, defaults to (0, 0)
            Position of the circle
        `radius`: int, defaults to 5
            Radius of the circle
        `filled`: list, default to False
            Can be used to specify a color for each vertex drawn.
    '''
    cdef tuple _pos
    cdef double _radius
    cdef int _need_build

    def __init__(self, **kwargs):
        kwargs.setdefault('type', 'line_loop')
        kwargs.setdefault('format', 'vv')
        self._pos = kwargs.setdefault('pos', (0, 0))
        self._radius = kwargs.setdefault('radius', 5)
        self._need_build = 1
        GraphicElement.__init__(self, **kwargs)
        f = kwargs.setdefault('filled', False)
        self.type = self._determine_type(f)

    cpdef build(self):
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

    cpdef draw(self):
        if self._need_build:
            self.build()
            self._need_build = 0
        GraphicElement.draw(self)

    def _get_radius(self):
        return self._radius
    def _set_radius(self, r):
        if self._radius == r:
            return False
        self._radius = r
        self._need_build = 1
        return True
    radius = property(_get_radius, _set_radius,
        doc='Radius of the circle (double)')

    def _determine_type(self, f):
        return 'polygon' if f else 'line_strip'
    def _get_filled(self):
        return True if self._type == GL_POLYGON else False
    def _set_filled(self, f):
        t = self._determine_type(f)
        if self.type == t:
            return False
        self.type = t
        self._need_build = 1
        return True
    filled = property(_get_filled, _set_filled,
        doc='Indicates whether the circle is filled or not')

    def _get_pos(self):
        return self._pos
    def _set_pos(self, pos):
        if pos == self._pos:
            return False
        self._pos = tuple(pos)
        self._need_build = 1
        return True
    pos = property(_get_pos, _set_pos,
        doc='Object position (x, y)')

    def _get_x(self):
        return self._pos[0]
    def _set_x(self, x):
        if x == self.pos[0]:
            return False
        self._pos = (x, self.y)
        self._need_build = 1
        return True
    x = property(_get_x, _set_x,
        doc = 'Object X position')

    def _get_y(self):
        return self._pos[1]
    def _set_y(self, y):
        if y == self.pos[1]:
            return False
        self._pos = (self.x, y)
        self._need_build = 1
        return True
    y = property(_get_y, _set_y,
        doc = 'Object Y position')


cdef class Color(GraphicInstruction):
    '''Define color to be used in the following (floats between 0 and 1) ::

        >>> c = Canvas()
        >>> c.color(1., 0.4, 0., 1.)
        >>> c.rectangle(pos=(50, 50), size=(100, 100))

        >>> c.draw()

    .. Note:
        Blending is activated if alpha value != 1

    :Parameters:
        `*color` : list
            Can have 3 or 4 float values (between 0 and 1)
        `sfactor` : opengl factor, default to GL_SRC_ALPHA
            Default source factor to be used if blending is activated
        `dfactor` : opengl factor, default to GL_ONE_MINUS_SRC_ALPHA
            Default destination factor to be used if blending is activated
        `blend` : boolean, default to None
            Set True if you really want to activate blending, even
            if the alpha color is 1 (which means no blending in theory)
    '''

    cdef int _blend
    cdef int _sfactor
    cdef int _dfactor
    cdef tuple _color

    def __cinit__(self):
        self._color = (0, 0, 0, 0)

    def __init__(self, *color, **kwargs):
        GraphicInstruction.__init__(self)

        self._blend = kwargs.get('blend', 0)
        self._sfactor = kwargs.get('sfactor', GL_SRC_ALPHA)
        self._dfactor = kwargs.get('dfactor', GL_ONE_MINUS_SRC_ALPHA)
        self.color = color

    cpdef draw(self):
        force_blend = self._blend == 1
        color = self._color
        ctx = self.context
        ctx.set('color', color)
        if color[3] == 1 and not force_blend:
            ctx.set('blend', 0)
        else:
            ctx.set('blend', 1)
            ctx.set('sfactor', self._sfactor)
            ctx.set('dfactor', self._dfactor)

    def _get_color(self):
        return self._color
    def _set_color(self, x):
        if self._color == x:
            return
        # convert to 4 integer
        l = len(x)
        if l == 1:
            x = (x[0], x[0], x[0], 1)
        elif l == 3:
            x = (x[0], x[1], x[2], 1)
        elif l == 4:
            pass
        else:
            raise Exception('Unsupported color format')
        self._color = tuple(x)
    color = property(_get_color, _set_color,
        doc='''Get/Set the color in tuple format (r, g, b, a)''')


cdef class CSSRectangle(GraphicInstruction):
    '''
    Construct a rectangle that supports a lot of CSS attributes.
    A CSSRectangle can also be constructed by giving values like ::

        # classical way
        >>> CSSRectangle(pos=(0, 0), size=(500, 500), style=self.style)

        # alternative way
        >>> CSSRectangle(x, y, w, h, style=self.style)

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
    cdef dict _style
    cdef str _prefix
    cdef str _state
    cdef list _objects
    cdef tuple _pos
    cdef tuple _size
    cdef int _need_build

    def __init__(self, *values, **kwargs):
        GraphicInstruction.__init__(self)

        self._objects = []
        self._style = kwargs.get('style', {})
        self._prefix = kwargs.get('prefix', None)
        self._state = kwargs.get('state', None)
        self._pos = tuple(kwargs.get('pos', (0, 0)))
        self._size = tuple(kwargs.get('size', (1, 1)))
        if len(values) == 4:
            x, y, w, h = values
            self._pos = x, y
            self._size = w, h
        elif len(values) != 0:
            raise Exception('CSSRectangle values must be passed like this: CSSRectangle(x, y, w, h)')

        self._need_build = 1

    cpdef build(self):
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
            overwrites = set()
            for s in style:
                if state in s:
                    overwrite  = s.replace(state, '')
                    newstyle[overwrite] = style[s]
                    overwrites.add(overwrite)
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

        roundrect = 0
        border_radius = style.get('border-radius', 0)
        if border_radius > 0:
            roundrect = 1
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

        # add border image object
        if style.get('draw-border-image', 0):
            texture = texture_lookup(style.get('border-image'))
            if texture is not None:
                k2 = k.copy()
                k2['borders'] = style.get('border-image-width', [0, 0, 0, 0])
                k2['texture'] = texture
                obj.append(ImageRectangle(**k2))

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

    cpdef draw(self):
        if self._need_build:
            self.build()
            self._need_build = 0
        for x in self._objects:
            x.draw()

    def _get_size(self):
        return self._size
    def _set_size(self, size):
        if self._size == size:
            return False
        self._size = tuple(size)
        self._need_build = 1
        return True
    size = property(_get_size, _set_size,
        doc='Object size (width, height)')

    def _get_width(self):
        return self._size[0]
    def _set_width(self, w):
        if self._size[0] == w:
            return False
        self._size = (w, self._size[1])
        self._need_build = 1
        return True
    width = property(_get_width, _set_width,
        doc='Object width')

    def _get_height(self):
        return self._size[1]
    def _set_height(self, h):
        if self._size[1] == h:
            return False
        self._size = (self._size[0], h)
        self._need_build = 1
        return True
    height = property(_get_height, _set_height,
        doc='Object height')

    def _get_pos(self):
        return self._pos
    def _set_pos(self, pos):
        if pos == self._pos:
            return False
        self._pos = tuple(pos)
        self._need_build = 1
        return True
    pos = property(_get_pos, _set_pos,
        doc='Object position (x, y)')

    def _get_x(self):
        return self._pos[0]
    def _set_x(self, x):
        if x == self.pos[0]:
            return False
        self._pos = (x, self.y)
        self._need_build = 1
        return True
    x = property(_get_x, _set_x,
        doc = 'Object X position')

    def _get_y(self):
        return self._pos[1]
    def _set_y(self, y):
        if y == self.pos[1]:
            return False
        self._pos = (self.x, y)
        self._need_build = 1
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


cdef class Canvas:
    '''Create a batch of graphic objects.
    Can be used to store many graphic instructions and call them for drawing.
    (Note: This will lead to optimizations in the near future.)
    '''

    cdef list _batch
    cdef GraphicContext _context

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
        '''Clear all the elements in the canvas'''
        self._batch = []

    def draw(self):
        '''Draw all the canvas elements'''
        #cdef GraphicInstruction x
        for x in self._batch:
            x.draw()

    def save(self):
        '''Push the current context to the stack'''
        self.add(GraphicContextSave())

    def restore(self):
        '''Restore the previous saved context'''
        self.add(GraphicContextRestore())

    property objects:
        def __get__(self):
            return self._batch

    # facilities to create object
    def graphicElement(self, *largs, **kwargs):
        return self.add(GraphicElement(*largs, **kwargs))

    def line(self, *largs, **kwargs):
        '''Create a Line() object and add it to the canvas.
        Check Line() for more information.'''
        return self.add(Line(*largs, **kwargs))

    def circle(self, *largs, **kwargs):
        '''Create a Circle() object and add it to the canvas.
        Check Circle() for more information.'''
        return self.add(Circle(*largs, **kwargs))

    def point(self, *largs, **kwargs):
        '''Create a Point() object and add it to the canvas.
        Check Point() for more information.'''
        return self.add(Point(*largs, **kwargs))

    def rectangle(self, *largs, **kwargs):
        '''Create a Rectangle() object and add it to the canvas.
        Check Rectangle() for more information.'''
        return self.add(Rectangle(*largs, **kwargs))

    def imageRectangle(self, *largs, **kwargs):
        '''Create a ImageRectangle() object and add it to the canvas.
        Check ImageRectangle() for more information.'''
        return self.add(ImageRectangle(*largs, **kwargs))

    def roundedRectangle(self, *largs, **kwargs):
        '''Create a RoundedRectangle() object and add it to the canvas.
        Check RoundedRectangle() for more information.'''
        return self.add(RoundedRectangle(*largs, **kwargs))

    def cssRectangle(self, *largs, **kwargs):
        '''Create a CSSRectangle() object and add it to the canvas.
        Check CSSRectangle() for more information.'''
        return self.add(CSSRectangle(*largs, **kwargs))

    def color(self, *largs, **kwargs):
        '''Create a Color() object and add it to the canvas.
        Check Color() for more information.'''
        return self.add(Color(*largs, **kwargs))

    def text(self, *largs, **kwargs):
        '''Create a Text() object and add it to the canvas.
        Check Text() for more information.'''
        return self.add(Text(*largs, **kwargs))

