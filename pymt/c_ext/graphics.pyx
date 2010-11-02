import os
from pymt import pymt_shader_dir
from pymt.logger import pymt_logger
from c_buffer cimport Buffer
from c_opengl cimport *
from pymt.lib.transformations import matrix_multiply, identity_matrix, rotation_matrix, translation_matrix, scale_matrix, clip_matrix
import numpy

cdef double pi = 3.1415926535897931
cdef extern from "math.h":
    double cos(double)
    double sin(double)
    double sqrt(double)


'''
Description of vertex attributes, standard format for shaders and vbo
'''
cdef list VERTEX_ATTRIBUTES = [ 
    {'name': 'vPosition',  'index':0, 'size': 2, 'type': GL_FLOAT, 'bytesize': sizeof(GLfloat)*2},
    {'name': 'vColor',     'index':1, 'size': 4, 'type': GL_FLOAT, 'bytesize': sizeof(GLfloat)*4},
    {'name': 'vTexCoord0', 'index':2, 'size': 2, 'type': GL_FLOAT, 'bytesize': sizeof(GLfloat)*2} 
] 

cdef struct vertex:
    GLfloat x
    GLfloat y
    GLfloat r
    GLfloat g
    GLfloat b
    GLfloat a
    GLfloat s
    GLfloat t

cdef vertex vertex8f(GLfloat x, GLfloat y, GLfloat r, GLfloat g, GLfloat b, GLfloat a, GLfloat s, GLfloat t):
    cdef vertex v
    v.x = x
    v.y = y
    v.r = r
    v.g = g
    v.b = b
    v.a = a
    v.s = s
    v.t = t
    return v

cdef vertex vertex6f(GLfloat x, GLfloat y, GLfloat r, GLfloat g, GLfloat b, GLfloat a):
    return vertex8f(x,y,r,g,b,a,0.0,0.0)

cdef vertex vertex5f(GLfloat x, GLfloat y, GLfloat r, GLfloat g, GLfloat b, GLfloat a):
    return vertex8f(x,y,r,g,b,1.0,0.0,0.0)
    
cdef vertex vertex2f(GLfloat x, GLfloat y):
    return vertex8f(x,y,1.0,1.0,1.0,1.0,0.0,0.0)


#TODO: create own matrix transforms

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

    def __cinit__(self, str vert_src, str frag_src):
        self.frag_src = frag_src
        self.vert_src = vert_src

    def __init__(self, str vert_src, str frag_src):
        self.program = glCreateProgram()
        self.bind_attrib_locations()
        self.build()

    #def __setitem__(self, str name, value):
    cpdef set_uniform(self, str name, value):    
        """pass a uniform variable to the shader"""
        py_byte_str = name.decode('UTF-8')
        cdef char* c_name = py_byte_str
        cdef GLint loc = glGetUniformLocation(self.program, c_name)
        cdef GLfloat mat[16]        

        
        if type(value) == numpy.ndarray:
            np_flat = numpy.ascontiguousarray(value.T, dtype='float32').flatten()
            #print "settgin matrix:", name, "[ ", 
            for i in range(16):
                mat[i] = <GLfloat>np_flat[i]
            #    print mat[i],
            glUniformMatrix4fv(loc, 1, False, mat) 
            #print "]"       
            return
        
        if type(value) == int:
            glUniform1i(loc, value)
            return
        if type(value) == float:
            glUniform1f(loc, value)
            return        
        
        cdef int vec_size = len(value)
        if type(value[0]) == float:
            if vec_size == 2:
                glUniform2f(loc, value[0], value[1])
            if vec_size == 3:
                glUniform3f(loc, value[0], value[1], value[2])
            if vec_size == 4:
                glUniform4f(loc, value[0], value[1], value[2], value[3])
        if type(value[0]) == int:
            if vec_size == 2:
                glUniform2i(loc, value[0], value[1])
            if vec_size == 3:
                glUniform3i(loc, value[0], value[1], value[2])
            if vec_size == 4:
                glUniform4i(loc, value[0], value[1], value[2], value[3])       

    cpdef use(self):
        '''Use the shader'''
        glUseProgram(self.program)
        
    cpdef stop(self):
        '''Stop using the shader'''
        glUseProgram(0)

    cdef bind_attrib_locations(self):
        cdef char* c_name
        for attr in VERTEX_ATTRIBUTES:
            c_name = attr['name']
            glBindAttribLocation(self.program, attr['index'], c_name)

    cdef build(self):
        self.vertex_shader = self.compile_shader(self.vert_src, GL_VERTEX_SHADER)
        self.fragment_shader = self.compile_shader(self.frag_src, GL_FRAGMENT_SHADER)
        glAttachShader(self.program, self.vertex_shader)
        glAttachShader(self.program, self.fragment_shader)
        glLinkProgram(self.program)
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
        glGetShaderInfoLog(	shader, 2048, &msg_len, msg)
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
        else:
            pymt_logger.debug('Shader compiled sucessfully')
    """
    cdef set_uniformfv(self, char* name, int size, float* values):
        cdef GLint loc = glGetUniformLocation(self.program, name)
        if size == 2:
            glUniform2fv(loc, values)
        if size == 3:
            glUniform3fv(loc, values)
        if size == 4:
            glUniform4fv(loc, values)

    cdef set_uniformiv(self, char* name, int size, int* values):
        cdef GLint loc = glGetUniformLocation(self.program, name)
        if size == 2:
            glUniform2iv(loc, values)
        if size == 3:
            glUniform3iv(loc, values)
        if size == 4:
            glUniform4iv(loc, values)
    """
_default_vertex_shader = open(os.path.join(pymt_shader_dir, 'default.vs')).read()
_default_fragment_shader = open(os.path.join(pymt_shader_dir, 'default.fs')).read()
_default_shader = Shader(_default_vertex_shader, _default_fragment_shader)



cdef class VBO:
    cdef GLuint id
    cdef int usage
    cdef int target
    cdef list format
    cdef Buffer data
    cdef bool need_upload
    cdef int vbo_size
    
    def __cinit__(self):
        self.usage  = GL_DYNAMIC_DRAW
        self.target = GL_ARRAY_BUFFER
        self.format = VERTEX_ATTRIBUTES
        self.need_upload = True
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
        self.need_upload = False

    cdef bind(self):
        if self.need_upload:
            if self.vbo_size == self.data.size():
                glBindBuffer(GL_ARRAY_BUFFER, self.id)
                glBufferSubData(GL_ARRAY_BUFFER, 0, self.data.size(), self.data.pointer())
            else:
                self.allocate_buffer()
            self.need_upload  = False
        else:
            glBindBuffer(GL_ARRAY_BUFFER, self.id)
               
        cdef int offset = 0
        for attr in self.format:
            glEnableVertexAttribArray(attr['index'])
            glVertexAttribPointer(attr['index'], attr['size'], attr['type'], GL_FALSE, sizeof(vertex), <GLvoid*>offset)
            offset += attr['bytesize']
             

    cpdef unbind(self):
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    cdef add_vertices(self, void *v, int* indices, int count):
        cdef int i
        self.need_upload = True        
        self.data.add(v, indices, count)

    cdef update_vertices(self, int index, vertex* v, int count):
        self.need_upload = True
        self.data.update(index, v, count)
        
    cdef remove_vertices(self, int* indices, int count):
        self.data.remove(indices, count)




cdef class Canvas:
    cdef VBO vertex_buffer
    cdef Buffer index_buffer
    cdef Shader shader
    cdef object mvm
    cdef object pm
    
    def __cinit__(self):
        self.shader = _default_shader
        self.pm = identity_matrix()
        self.mvm = identity_matrix()
        self.vertex_buffer = VBO()
        self.index_buffer = Buffer(sizeof(GLint))

    cpdef draw(self):
        self.shader.use()
        self.shader.set_uniform('projection_mat', self.pm)
        self.shader.set_uniform('modelview_mat', self.mvm)
        self.index_buffer.pack()   
        self.vertex_buffer.bind() 
        #glBindBuffer(GL_ARRAY_BUFFER, 0)
        attr = VERTEX_ATTRIBUTES[0]
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer.id)
        #glEnableVertexAttribArray(attr['index'])
        #glVertexAttribPointer(attr['index'], attr['size'], attr['type'], GL_FALSE, sizeof(vertex), <GLvoid*>0)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_buffer.data.count())    
        #glBindBuffer(GL_ARRAY_BUFFER, 0)  
        #glDrawElements(GL_TRIANGLES, self.index_buffer.count(), GL_UNSIGNED_BYTE, <GLvoid*>self.index_buffer.pointer());
        




cdef class rectangle:
    cdef Canvas canvas
    cdef bool initialized    
    cdef int v_indices[4]
    cdef float x
    cdef float y
    cdef float w
    cdef float h

    def __init__(self, canvas, **kwargs):
        self.initialized = False
        self.canvas = canvas
        pos  = kwargs.get('pos', (0,0))
        size = kwargs.get('size', (1,1))
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]
        self.set_rectangle()

        

    cdef set_rectangle(self):
        cdef vertex a = vertex2f(self.x,        self.y)
        cdef vertex b = vertex2f(self.x+self.w, self.y)
        cdef vertex c = vertex2f(self.x+self.w, self.y+self.h)
        cdef vertex d = vertex2f(self.x,        self.y+self.h)
        self.set_vertices(a, b, c, d)

    cdef set_vertices(self, vertex a, vertex b, vertex c, vertex d):
        cdef vertex v_data[4]        
        v_data[0] = a
        v_data[1] = b
        v_data[2] = c
        v_data[3] = d  
        self.set_vertex_data(v_data)  

    cdef set_vertex_data(self, vertex* v_data):
        print "set vertex data"
        if self.initialized:
            return self.update_vertex_data(v_data) 

        print "setting for first time"
        self.canvas.vertex_buffer.add_vertices(v_data, self.v_indices, 4)
        print ">>>>>", self.canvas.vertex_buffer.data.count()        
        print "added verts.  indices:", <long>self.v_indices, <int>self.v_indices[0], self.v_indices[1], self.v_indices[2], self.v_indices[3]
        self.canvas.index_buffer.add(self.v_indices,     NULL, 3) # 0, 1, 2
        self.canvas.index_buffer.add(&self.v_indices[2], NULL, 2) # 2, 3
        self.canvas.index_buffer.add(self.v_indices,     NULL, 1) # 0
        print "#########", self.canvas.index_buffer.count()
        print "added verts.  indices:", <long>self.v_indices, <int>self.v_indices[0], self.v_indices[1], self.v_indices[2], self.v_indices[3]
        self.initialized = True

    cdef update_vertex_data(self, vertex* v_data):
        print "update vertex data"
        self.canvas.vertex_buffer.update_vertices(self.v_indices[0],  v_data, 4 )     
        self.canvas.vertex_buffer.update_vertices(self.v_indices[1],  &v_data[1], 1 ) 
        self.canvas.vertex_buffer.update_vertices(self.v_indices[2],  &v_data[2], 1 ) 
        self.canvas.vertex_buffer.update_vertices(self.v_indices[3],  &v_data[3], 1 )    


