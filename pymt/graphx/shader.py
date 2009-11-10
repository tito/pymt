'''
Shader: abstract compilation and usage
'''

__all__ = ['ShaderException', 'Shader']

import pymt
import ctypes as c
from OpenGL.GL import *
from OpenGL.GLU import *

class ShaderException(Exception):
    '''Exception launched by shader in error case'''
    pass

class Shader(object):
    '''Create a vertex or fragment shader

    :Parameters:
        `vertex_source` : string, default to None
            Source code for vertex shader
        `fragment_source` : string, default to None
            Source code for fragment shader
    '''
    def __init__(self, vertex_source=None, fragment_source=None):
        self.program = glCreateProgram()

        if vertex_source:
            self.vertex_shader = self.create_shader(vertex_source,GL_VERTEX_SHADER)
            glAttachShader(self.program, self.vertex_shader)

        if fragment_source:
            self.fragment_shader = self.create_shader(fragment_source,GL_FRAGMENT_SHADER)
            glAttachShader(self.program, self.fragment_shader)

        glLinkProgram(self.program)
        message = self.get_program_log(self.program)
        if message:
            pymt.pymt_logger.debug('shader message: %s' % message)

    def create_shader(self, source, shadertype):
        sbuffer = c.create_string_buffer(source)
        pointer = c.cast(c.pointer(c.pointer(sbuffer)),
                         c.POINTER(c.POINTER(c.c_char)))
        nulll = c.POINTER(c.c_long)()
        shader = glCreateShader(shadertype)
        glShaderSource(shader, 1, pointer, None)
        glCompileShader(shader)
        message = self.get_shader_log(shader)
        if message:
            pymt.pymt_logger.debug('shader message: %s' % message)
        return shader

    def set_uniform_f(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniform1f(location, value)

    def set_uniform_i(self, name, value):
        location = glGetUniformLocation(self.program, name)
        glUniform1i(location, value)

    def __setitem__(self, name, value):
        """pass a variable to the shader"""
        if isinstance(value, float):
            self.set_uniform_f(name, value)
        elif isinstance(value, int):
            self.set_uniform_i(name, value)
        else:
            raise TypeError("Only single floats and ints are supported so far")

    def use(self):
        '''Use the shader'''
        glUseProgram(self.program)

    def stop(self):
        '''Stop using the shader'''
        glUseProgram(0)

    def get_shader_log(self, shader):
        '''Return the shader log'''
        return self.get_log(shader, glGetShaderInfoLog)

    def get_program_log(self, shader):
        '''Return the program log'''
        return self.get_log(shader, glGetProgramInfoLog)

    def get_log(self, obj, func):
        log_buffer = c.create_string_buffer(4096)
        buffer_pointer = c.cast(c.pointer(log_buffer), c.POINTER(c.c_char))
        written = c.c_int()
        func(obj, 4096, c.pointer(written), buffer_pointer)
        return log_buffer.value

