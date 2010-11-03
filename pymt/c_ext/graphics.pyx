import os
from pymt import pymt_shader_dir
from pymt.logger import pymt_logger
from pymt.resources import resource_find

from c_buffer cimport Buffer
from c_opengl cimport *

#TODO, see which ones we have to write in cython directlym e.g. transformations, texture etc.
from pymt.core.image import Image
import numpy
from pymt.lib.transformations import matrix_multiply, identity_matrix, \
             rotation_matrix, translation_matrix, scale_matrix





'''
standard math definitions
'''
cdef double pi = 3.1415926535897931
cdef extern from "math.h":
    double cos(double)
    double sin(double)
    double sqrt(double)

cdef struct vertex:
    GLfloat x, y
    GLfloat s0, t0 
    GLfloat s1, t1
    GLfloat s2, t2

cdef vertex vertex8f(GLfloat x, GLfloat y, GLfloat s0, GLfloat t0, GLfloat s1, GLfloat t1, GLfloat s2, GLfloat t2):
    cdef vertex v
    v.x  = x;   v.y  = y
    v.s0 = s0;  v.t0 = t0
    v.s1 = s1;  v.t1 = t1
    v.s2 = s2;  v.t2 = t2
    return v

cdef vertex vertex6f(GLfloat x, GLfloat y, GLfloat s0, GLfloat t0, GLfloat s1, GLfloat t1):
    return vertex8f(x,y,s0,t0,s1,t1,0.0,0.0)

cdef vertex vertex4f(GLfloat x, GLfloat y, GLfloat s0, GLfloat t0):
    return vertex8f(x,y,s0,t0,0.0,0.0,0.0,0.0)
    
cdef vertex vertex2f(GLfloat x, GLfloat y):
    return vertex8f(x,y,0.0,0.0,0.0,0.0,0.0,0.0)

'''
Description of vertex attributes, standard format for shaders and vbo
'''
cdef list VERTEX_ATTRIBUTES = [ 
    {'name': 'vPosition',  'index':0, 'size': 2, 'type': GL_FLOAT, 'bytesize': sizeof(GLfloat)*2, 'per_vertex': True},
    {'name': 'vTexCoord0', 'index':1, 'size': 2, 'type': GL_FLOAT, 'bytesize': sizeof(GLfloat)*2, 'per_vertex': True},
    {'name': 'vTexCoord1', 'index':2, 'size': 2, 'type': GL_FLOAT, 'bytesize': sizeof(GLfloat)*2, 'per_vertex': True}, 
    {'name': 'vTexCoord2', 'index':3, 'size': 2, 'type': GL_FLOAT, 'bytesize': sizeof(GLfloat)*2, 'per_vertex': True}, 
    {'name': 'vColor',     'index':4, 'size': 4, 'type': GL_FLOAT, 'bytesize': sizeof(GLfloat)*4, 'per_vertex': False} 
] 






cdef int ACTIVE_SHADER = 0

cdef class Shader:
    '''Create a vertex or fragment shader

    :Parameters:
        `vert_src` : string 
            source code for vertex shader
        `frag_src` : string
            source code for fragment shader
    '''
    cdef int program
    cdef int vertex_shader
    cdef int fragment_shader
    cdef object vert_src
    cdef object frag_src 
    cdef dict uniform_locations 
    cdef dict uniform_values

    def __cinit__(self, str vert_src, str frag_src):
        self.frag_src = frag_src
        self.vert_src = vert_src
        self.uniform_locations = dict()
        self.uniform_values = dict()

    def __init__(self, str vert_src, str frag_src):
        self.program = glCreateProgram()
        self.bind_attrib_locations()
        self.build()
        
    cdef int get_uniform_loc(self, str name):
        name_byte_str = name
        cdef char* c_name = name_byte_str
        cdef int loc = glGetUniformLocation(self.program, c_name)
        self.uniform_locations[name] = loc
        return loc

    #def __setitem__(self, str name, value):
    cpdef set_uniform(self, str name, value):
        self.uniform_values[name] = value

    cpdef upload_uniform(self, str name, value):
        """pass a uniform variable to the shader"""
        cdef int vec_size, loc
        val_type = type(value)        
        loc = self.uniform_locations.get(name, self.get_uniform_loc(name))
    

        #TODO: use cython matrix transforms
        if val_type == numpy.ndarray:
            self.set_uniform_matrix(name, value)
        elif val_type == int:
            glUniform1i(loc, value)
        elif val_type == float:
            glUniform1f(loc, value)
        else:  
            #must have been a list, tuple, or other sequnce ot be a vector uniform
            val_type = type(value[0])
            vec_size = len(value)
            if val_type == float:
                if vec_size == 2:
                    glUniform2f(loc, value[0], value[1])
                elif vec_size == 3:
                    glUniform3f(loc, value[0], value[1], value[2])
                elif vec_size == 4:
                    glUniform4f(loc, value[0], value[1], value[2], value[3])
            elif val_type == int:
                if vec_size == 2:
                    glUniform2i(loc, value[0], value[1])
                elif vec_size == 3:
                    glUniform3i(loc, value[0], value[1], value[2])
                elif vec_size == 4:
                    glUniform4i(loc, value[0], value[1], value[2], value[3])       


    cdef set_uniform_matrix(self, str name, value):
        #TODO: use cython matrix transforms
        cdef int loc = self.uniform_locations.get(name, self.get_uniform_loc(name))
        cdef GLfloat mat[16] 
        np_flat = numpy.ascontiguousarray(value.T, dtype='float32').flatten()
        for i in range(16):
            mat[i] = <GLfloat>np_flat[i]
        glUniformMatrix4fv(loc, 1, False, mat) 

    cpdef use(self):
        '''Use the shader'''
        if ACTIVE_SHADER == self.program:
            return
        glUseProgram(self.program)
        for k,v in self.uniform_values.iteritems():
            self.upload_uniform(k, v)
        
    cpdef stop(self):
        '''Stop using the shader'''
        glUseProgram(0)

    cdef bind_attrib_locations(self):
        cdef char* c_name
        for attr in VERTEX_ATTRIBUTES:
            c_name = attr['name']
            glBindAttribLocation(self.program, attr['index'], c_name)
            if attr['per_vertex']:
                glEnableVertexAttribArray(attr['index'])

    cdef build(self):
        self.vertex_shader = self.compile_shader(self.vert_src, GL_VERTEX_SHADER)
        self.fragment_shader = self.compile_shader(self.frag_src, GL_FRAGMENT_SHADER)
        glAttachShader(self.program, self.vertex_shader)
        glAttachShader(self.program, self.fragment_shader)
        glLinkProgram(self.program)
        self.uniform_locations = dict()
        self.process_build_log()

    cdef compile_shader(self, char* source, shadertype):
        shader = glCreateShader(shadertype)
        glShaderSource(shader, 1, <GLchar**> &source, NULL)
        glCompileShader(shader)
        return shader

    cdef get_shader_log(self, shader):
        '''Return the shader log'''
        cdef int msg_len
        cdef char msg[2048]
        glGetShaderInfoLog(shader, 2048, &msg_len, msg)
        return msg

    cdef get_program_log(self, shader):
        '''Return the program log'''
        cdef int msg_len
        cdef char msg[2048]
        glGetProgramInfoLog(shader, 2048, &msg_len, msg)
        return msg

    cdef process_build_log(self):
        message = self.get_program_log(self.program)
        if message:
            pymt_logger.error('Shader: shader program message: %s' % message)
            raise Exception(message)
        else:
            pymt_logger.debug('Shader compiled sucessfully')
    
_default_vertex_shader = open(os.path.join(pymt_shader_dir, 'default.vs')).read()
_default_fragment_shader = open(os.path.join(pymt_shader_dir, 'default.fs')).read()
_default_shader = Shader(_default_vertex_shader, _default_fragment_shader)



cdef class GraphicContext:
    '''Handle the saving/restore of the context

    TODO: explain more how it works
    '''
    cdef dict state
    cdef list stack
    cdef set journal
    cdef readonly int need_flush

    property default_shader:
        def __get__(self):
            return _default_shader

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
        self.set('shader', self.default_shader)
        self.set('projection_mat', identity_matrix())
        self.set('modelview_mat', identity_matrix())
        self.set('color', (1.0, 1.0, 1.0, 1.0) )
        self.set('blend', 0)
        self.set('blend_sfactor', GL_SRC_ALPHA)
        self.set('blend_dfactor', GL_ONE_MINUS_SRC_ALPHA)
        self.set('linewidth', 1)
        #self.set('texture0', 0)

    cpdef save(self):
        self.stack.append(self.state.copy())

    cpdef restore(self):
        newstate = self.stack.pop()
        state = self.state
        for k, v in newstate.iteritems():
            if not state[k] is v:
                self.set(k, v)
    
    cpdef translate(self, double x, double y, double z):
        t = translation_matrix(x, y, z)
        mat = matrix_multiply(self.get('modelview_mat'), t)
        self.set('modelview_mat', mat)

    cpdef scale(self, double s):
        t = scale_matrix(s)
        mat = matrix_multiply(self.get('modelview_mat'), t)
        self.set('modelview_mat', mat)
        
    cpdef rotate(self, double angle, double x, double y, double z):
        t = rotation_matrix(angle, [x, y, z])
        mat = matrix_multiply(self.get('modelview_mat'), t)
        self.set('modelview_mat', mat)

    cpdef flush(self):
        # activate all the last changes done on context
        # apply all the actions in the journal !
        cdef dict state
        cdef set journal
        cdef str x

        self.state['shader'].use()
        
        if not self.journal:
            return

        state = self.state
        journal = self.journal
        for x in journal:
            value = state[x]
            if x == 'color':
                glVertexAttrib4f(4, value[0], value[1], value[2], value[3]) #vColor
            
            elif x == 'blend':
                if value:   glEnable(GL_BLEND)
                else:       glDisable(GL_BLEND)
            
            elif x in ('blend_tem.texture:sfactor', 'blend_dfactor'):
                glBlendFunc(state['blend_sfactor'], state['blend_dfactor'])
         
            elif x != 'shader': #set uniform variable
                #print "setting uniform", x, value
                self.state['shader'].set_uniform(x, value)

        journal.clear()
        self.need_flush = 0

_default_context = GraphicContext()




cdef class VBO:
    cdef GLuint id
    cdef int usage
    cdef int target
    cdef list format
    cdef Buffer data
    cdef int need_upload
    cdef int vbo_size
    
    def __cinit__(self):
        self.usage  = GL_DYNAMIC_DRAW
        self.target = GL_ARRAY_BUFFER
        self.format = VERTEX_ATTRIBUTES
        self.need_upload = 1
        self.vbo_size = 0
    
    def __init__(self, **kwargs):
        self.format = kwargs.get('format', self.format)
        self.data = Buffer(sizeof(vertex))
        self.create_buffer()

    cdef create_buffer(self):
        glGenBuffers(1, &self.id)
        self.allocate_buffer()

    cdef allocate_buffer(self):
        self.vbo_size = self.data.size()
        glBindBuffer(GL_ARRAY_BUFFER, self.id)
        glBufferData(GL_ARRAY_BUFFER, self.vbo_size, self.data.pointer(), self.usage)
        self.need_upload = 0

    cdef update_buffer(self):
        if self.vbo_size < self.data.size():
            self.allocate_buffer()
        elif self.need_upload:
            glBindBuffer(GL_ARRAY_BUFFER, self.id)
            glBufferSubData(GL_ARRAY_BUFFER, 0, self.data.size(), self.data.pointer())
            self.need_upload  = 0

    cdef bind(self):
        self.update_buffer()
        glBindBuffer(GL_ARRAY_BUFFER, self.id)
        #glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, sizeof(vertex), <GLvoid*>0) #vPosition
        #glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, sizeof(vertex), <GLvoid*>(2*sizeof(GLfloat))) #vTexCoord0
        #glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, sizeof(vertex), <GLvoid*>(4*sizeof(GLfloat))) #vTexCoord1
        #glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, sizeof(vertex), <GLvoid*>(6*sizeof(GLfloat))) #vTexCoord2
        cdef int offset = 0
        for attr in self.format:
            if not attr['per_vertex']:
                continue
            glVertexAttribPointer(attr['index'], attr['size'], attr['type'], GL_FALSE, sizeof(vertex), <GLvoid*>offset)
            offset += attr['bytesize']

    cpdef unbind(self):
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    cdef add_vertices(self, void *v, int* indices, int count):
        cdef int i
        self.need_upload = 1
        self.data.add(v, indices, count)

    cdef update_vertices(self, int index, vertex* v, int count):
        self.need_upload = 1
        self.data.update(index, v, count)
        
    cdef remove_vertices(self, int* indices, int count):
        self.data.remove(indices, count)


canvas_statement = None
cdef class Canvas:
    cdef GraphicContext _context
    cdef VBO vertex_buffer
    cdef list batch
    cdef int need_compile
    cdef list texture_map
    cdef list batch_slices

    def __cinit__(self):
        self._context = _default_context
        self.vertex_buffer = VBO()
        self.batch = []
        self.need_compile = 1
        self.texture_map = []
        self.batch_slices = []

    property context:
        def __get__(self):
            return self._context

    cpdef __enter__(self):
        global canvas_statement
        canvas_statement = self

    cpdef __exit__(self, extype, value, traceback):
        global canvas_statement
        canvas_statement = None

    cdef add(self, element, vertices):
        self.need_compile = 1
        self.batch.append((element, vertices))

    cdef remove(self, element):
        pass

    cdef compile(self):
        cdef int slice_start = -1
        cdef int slice_stop = -1
        cdef int i
        cdef object item

        self.compile_init()

        for i in xrange(len(self.batch)):
            item = self.batch[i]
            if isinstance(item[0], GraphicElement) :
                if slice_start == -1:
                    slice_start = slice_stop = i
                else:
                    slice_stop = i
            else:
                if slice_start != -1:
                    self.compile_slice('draw', slice_start, slice_stop)
                    slice_start = slice_stop = -1
                self.batch_slices.append(('instruction', item))
        if slice_start != -1:
            self.compile_slice('draw', slice_start, slice_stop)


    cpdef compile_init(self):
        self.texture_map = []
        self.batch_slices = []

    cpdef compile_slice(self, str command, slice_start, slice_end):
        cdef Buffer b = Buffer(sizeof(GLint))
        cdef int v
        cdef GraphicElement item
        cdef object bound_texture = None
        for item, vertices in self.batch[slice_start:slice_end+1]:  
            for v in vertices:  # add the vertices for this item
                b.add(&v, NULL, 1)
            if item.texture == bound_texture: #the same, sweet, keep going
                continue
            elif item.texture and item.texture != bound_texture:  #nope..muts bind the new texture 
                self.batch_slices.append(('instruction', BindTexture(item.texture)))
                self.batch_slices.append((command, b))
                b = Buffer(sizeof(GLint))
            else: #no item.texture..must unbind bound_texture and start new slice
                self.batch_slices.append(('instruction', UnbindTexture()))
                self.batch_slices.append((command, b))
                b = Buffer(sizeof(GLint))

        if b.count() > 0:  # last slice, all done, only have to add if there is actually somethign in it
            self.batch_slices.append((command, b))


    cpdef draw(self): 
        cdef int i
        cdef Buffer b

        if self.need_compile:
            self.compile()
            print "Done Compiling", self.batch_slices
            self.need_compile = 0


        self.context.flush()
        self.vertex_buffer.bind() 
        attr = VERTEX_ATTRIBUTES[0]
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer.id)
        for command, item in self.batch_slices:
            if command == 'draw':
                self.context.flush()
                b = item
                glDrawElements(GL_TRIANGLES, b.count(), GL_UNSIGNED_INT, b.pointer())
            elif command == 'instruction':
                (<GraphicInstruction>item).apply(self)
                
        glUseProgram(0)

        # XXX FIXME Maybe reset ?

cdef class GraphicElement:
    cdef Canvas canvas       #canvas in which to draw
    cdef VBO vbo             #vertex buffer
    cdef int v_count         #vertex cound
    cdef object texture

    def __cinit__(self):
        self.texture = None


cdef class GraphicInstruction:
    cdef apply(self, Canvas c):
        pass


cdef class BindTexture(GraphicInstruction):
    cdef object texture

    def __cinit__(self, texture):
        self.texture = texture

    cdef apply(self, Canvas c): 
        texture = self.texture
        glActiveTexture(GL_TEXTURE0)
        #print "enable texture"
        glEnable(texture.target)
        glBindTexture(texture.target, texture.id)
        c.context.set('texture0', 0)



cdef class UnbindTexture(GraphicInstruction):
    cdef apply(self, Canvas c): 
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)



cdef class Rectangle(GraphicElement):
    cdef vertex v_data[4]    #vertex data
    cdef int v_indices[4]    #indices in vbo for this rect
    cdef float v_tcoords[8] #texture coordinates
    cdef float x, y      #position
    cdef float w, h      #size
 
    def __init__(self, **kwargs):       
        GraphicElement.__init__(self, **kwargs)
        if canvas_statement is None:
            raise ValueError('Canvas must be bound')
        self.canvas = canvas_statement
        self.vbo = self.canvas.vertex_buffer
        pos  = kwargs.get('pos', (0,0))
        size = kwargs.get('size', (1,1))
        txc  = kwargs.get('tex_coords', (0.0,0.0, 1.0,0.0, 1.0,1.0, 0.0,1.0))
        self.texture = kwargs.get('texture', None)
        
        #initialize rectangle data
        self.x = pos[0];  self.y = pos[1]
        self.w = size[0]; self.h = size[1]
        for i in range(8):
            self.v_tcoords[i] = txc[i]

        #build vertices, allocate in vbo, and remeber indices
        self.v_count = 4
        self.build_rectangle()
        self.vbo.add_vertices(self.v_data, self.v_indices, 4)

        cdef list indices
        indices = [
            self.v_indices[0],
            self.v_indices[1],
            self.v_indices[2],
            self.v_indices[2],
            self.v_indices[3],
            self.v_indices[0],
        ]
        self.canvas.add(self, indices)

    cdef build_rectangle(self):
        '''
        Sets the vertex data, based on pos/size and tex_coords
        '''
        cdef float x,y,w,h
        cdef float* tc = self.v_tcoords
        cdef vertex *v
        x = self.x; y = self.y; w = self.w; h = self.h; 
        v = &self.v_data[0]
        v.x = x; v.y = y; v.s0 = tc[0]; v.t0 = tc[1]
        v = &self.v_data[1]
        v.x = x + w; v.y = y; v.s0 = tc[2]; v.t0 = tc[3]
        v = &self.v_data[2]
        v.x = x+ w; v.y = y + h; v.s0 = tc[4]; v.t0 = tc[5]
        v = &self.v_data[3]
        v.x = x; v.y = y+ h; v.s0 = tc[6]; v.t0 = tc[7]


    cdef update_vertex_data(self):
        '''
        Updates the vertex data in the vbo of the associated canvas
        '''
        cdef vertex* v_data = self.v_data
        cdef int* v_index = self.v_indices
        self.build_rectangle()
        self.vbo.update_vertices(v_index[0], &v_data[0], 1)     
        self.vbo.update_vertices(v_index[1], &v_data[1], 1) 
        self.vbo.update_vertices(v_index[2], &v_data[2], 1) 
        self.vbo.update_vertices(v_index[3], &v_data[3], 1)


    property pos:
        def __get__(self):
            return (self.x, self.y)
        def __set__(self, pos):
            self.x = pos[0]
            self.y = pos[1]
            self.update_vertex_data()
        
    property size:
        def __get__(self):
            return (self.w, self.h)
        def __set__(self, size):
            self.w = size[0]
            self.h = size[1]
            self.update_vertex_data()
 
    property tex_coords:
        def __get__(self):
            cdef float* t = self.v_tcoords
            return (t[0],t[1],t[2],t[3],t[4],t[5],t[6],t[7])
        def __set__(self, txc):
            for i in range(8):
                self.v_tcoords[i] = txc[i]
            self.update_vertex_data()   

      
