
from c_buffer cimport Buffer
from c_opengl cimport *


cdef double pi = 3.1415926535897931
cdef extern from "math.h":
    double cos(double)
    double sin(double)
    double sqrt(double)



"""
cdef struct Vertex:
    float x, y
    float r,g,b,a
    float s,t


cdef stuct VertexAttribute:
    int size
    int index
    

cdef dict VERTEX_ATTRIBUTES = {
    'vPosition'  :  VertexAttribute
    'vColor'     :
    'vTexCoord0' :  
}
"""

cdef class VBO:
    '''
    :Parameters:
        `format` : tuple of tuples, describes the vertex data format
            default is (('vPosition', 2), ('vColor', 2), ('TexCoord', 2))       
    '''
    cdef int usage

    cdef tuple format
    cdef int vertex_size
    cdef int num_attributes

    cdef GLuint id
    cdef Buffer data
    cdef bool need_upload
    
    def __cinit__(self):
        self.usage  = GL_DYNAMIC_DRAW
        self.target = GL_ARRAY_BUFFER
        self.format = (2,4,2)
        self.num_attributes = 3
        self.vertex_size = 8
        self.need_upload = True

    def __init__(self, **kwargs):
        self.format = kwargs.get('format', self.format)
        self.num_attributes = len(self.format)
        self.vertex_size = 0 
        cdef int i = 0
        for i in range(self.num_attributes):
            self.vertex_size = self.format[i][1]

        self.data = Buffer(sizeof(GLfloat) * self.vertex_size)
        self.create_buffer()

    cdef create_buffer(self):
        glGenBuffers(1, &self.id)
        self.allocate_buffer()

    cdef allocate_buffer(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.id)
        glBufferData(GL_ARRAY_BUFFER, self.data.size(), self.data.pointer(), self.usage)
        self.need_upload = False

    cdef bind(self):
        cdef int ptr
        glBindBuffer(GL_ARRAY_BUFFER, self.id)

        if self.need_upload:
            glBufferSubData(GL_ARRAY_BUFFER, 0, self.data.size(), self.data.pointer())
            self.need_upload  = False

        cdef int offset = 0
        cdef int attr_size = 0     
        cdef int i = 0   
        for i in range(self.num_attributes):
            attr_size = self.format[i][1]
            glEnableVertexAttribArray(i)
            glVertexAttribPointer(i, attr_size, GL_FLOAT, GL_FALSE, self.vertex_size, <GLvoid*>offset) 
            offset += attr_size

    cpdef unbind(self):
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    cdef list add_vertex(self, void *v, int count):
        self.need_upload = True        
        return self.data.add(v, count)
        

    cdef remove_vertices(self, list indices):
        self.data.remove(indices)
        


from pymt.logger import pymt_logger
import numpy #TODO: remove dependency by using cutom matrix class

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


    def __init__(self, str vert_src, str frag_src):
        self.program = glCreateProgram()

        glBindAttribLocation(self.program, 0, 'vPosition')
        glBindAttribLocation(self.program, 1, 'vColor')
        glBindAttribLocation(self.program, 2, 'vTexCoord0')
        glBindAttribLocation(self.program, 3, 'vTexCoord1')
        glBindAttribLocation(self.program, 4, 'vTexCoord2')
        glBindAttribLocation(self.program, 5, 'vTexCoord3')

        if vert_src:
            self.vertex_shader = self.compile_shader(vert_src, GL_VERTEX_SHADER)
            glAttachShader(self.program, self.vertex_shader)
        if vert_src:
            self.fragment_shader = self.compile_shader(frag_src, GL_FRAGMENT_SHADER)
            glAttachShader(self.program, self.fragment_shader)

        glLinkProgram(self.program)
        
        message = self.get_program_log(self.program)
        if message:
            pymt_logger.error('Shader: shader program message: %s' % message)
        else:
            pymt_logger.debug('Shader compiled sucessfully')

    cpdef compile_shader(self, str source, shadertype):
        cdef char* c_source = source
        shader = glCreateShader(shadertype)
        glShaderSource(shader, 1, &c_source, NULL)
        glCompileShader(shader)
        return shader

    def __setitem__(self, str uniform_name, value):
        """pass a variable to the shader"""

        cdef char* name = uniform_name
        location = glGetUniformLocation(self.program, name)
        
        if type(value) == numpy.ndarray:
            mat_gl = numpy.ascontiguousarray(value.T, dtype='float32').flatten()
            glUniformMatrix4fv(location, 1, False, mat_gl)        
            return
        
        if type(value) == int:
            glUniform1i(location, value)
            return
        
        value = map(float, value)
        if len(value) == 1:
            glUniform1f(location, float(value))
        elif len(value) == 2:
            glUniform2f(location, *value)
        elif len(value) == 3:
            glUniform3f(location, *value)
        elif len(value) == 4:
            glUniform4f(location, *value)
        

    cdef use(self):
        '''Use the shader'''
        glUseProgram(self.program)
        
    cdef stop(self):
        '''Stop using the shader'''
        glUseProgram(0)

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








 

